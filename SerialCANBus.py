
import serial
import struct
import os
import time

class SerialCANBus(object):
    '''
    This class takes in a list of dicts that define CAN frames that are to be sent over the 
        car's CAN bus via the Macchina M2 (https://www.macchina.cc) running M2RET (https://github.com/collin80/M2RET).
    The frames are sent at a regular interval and the responses are recorded to a csv file.
    The time saved in the csv should match the time the event happened on the bus, but in 
        the recording computer's epoch time. IE it takes the reported time from the M2 and
        modifies it by an offset to match the computers time.

    To get the M2 to send CAN data back in binary send it b'\xe7'
        If you do not send this it will send can data in ascii and some other data in binary such as time

    Get the time on M2:
        Send: b'\xf1\x01'
        Recieve: b'\xf1\x01<4 bytes to be read as uint32 as micro seconds since M2 boot>'
            Get to seconds with: struct.unpack('I',rawData[2:6])[0]/1e6

    Send CAN Frame: 
        Send:
        |  byte range  |  data type  |  Value  |  description
        |      0       |     NA      |   0xf1  |  start of packet
        |      1       |     int     |    -    |  0x00 indicates it is a canbus frame
        |     2-5      |     hex     |    -    |  CAN ID ( 4 bytes)
        |      6       |     int     |   0x00  |  Bus to send on, 0 = CAN0, 1 = CAN1, 2 = SWCAN, 3 = LIN1, 4 = LIN2
        |      7       |     int     |    -    |  length of data
        |     8+       |     NA      |    -    |  data bytes

    Received CAN Frame (when using binary mode):
        Definition of a CAN frame that is streamed over serial by M2
        |  byte range  |  data type  |  Value  |  description
        |      0       |     NA      |   0xf1  |  start of packet
        |      1       |     int     |    -    |  0x00 indicates it is a canbus frame
        |     2-5      |    uint32   |    -    |  time the message was recored in microseconds since boot
        |     6-9      |    uint32   |    -    |  CAN ID, convert the uint32 to hex to get the standard name
        |     10       |     int     |    -    |  indicates how many data bytes there are.
        |    11-18     |     hex     |    -    |  data, first 4 bytes are typically a descriptor, last 4 are data, can be 0 padded
        |     19       |     NA      |   0x00  |  can be a check sum, but for M2ret it is just 0
    '''

    def __init__(self,outputFile,CANData=[],serialBusName=""):
        '''
            outputFile: the csv file to save data to.
            CANData: list of dicts that define all the packets we are sending
                        [{"id":b'<4 byte CAN id as bytes>',"data":<bytes to request>}]
            serialBus: The bus that the M2 is attached to. If nothing is provided it will attempt to connect to the first bus
                        listed in /dev/ttyACM*
            
        '''
        # when CAN data is requested, the data is typically returned with and id of 8 bytes higher
        # this is the case for most cars, but not all
        self.returnDataOffset = 8 
        
        # inorder to not completely spam the CAN bus, we want to rate limit the requests for data
        # this is the time in seconds that must pass between each data send
        self.rateLimit = 0.1
        self.lastDataSend = 0 # record the last time.time() we requested data

        self.outputFile = outputFile
        self.CANData = CANData
        self.serialBusName = serialBusName

        self.data = b''
        self.parsedCANData = []

        self._convertCANDataToCANRequestPackets()
        self._initializeM2() # create self.serial, set timeOffset

        # make sure the output directory exists
        fileDir = outputFile[:outputFile.rfind("/")]
        if not os.path.isdir(fileDir):
            os.makedirs(fileDir)

        print("__init__() done")

    def _initializeM2(self):
        '''
        initialize the M2
        '''
        if self.serialBusName == "":
            self.serialBusName = self._findBus()
        assert self.serialBusName != "", "No device found at /dev/ttyACM*"

        print("Starting serial communication with M2...")
        self.serial = serial.Serial(self.serialBusName,1152000,timeout=0)
        #self.serial.write(b'\xe7') # tell M2RET to respond in binary, not using this because it is easier to just read ascii
        time.sleep(2) # Let the M2 boot and dump all its boot info to serial
        self.serial.read_all() # then read it all to clear it

        self._updateTimeOffset()

        print("Finished initialization!")

    def _findBus(self):
        '''
            Attempt to find a bus to connect to
        '''
        allBusNames = os.listdir("/dev/")
        matchingBuses = [x for x in allBusNames if "ttyACM" in x]
        
        if len(matchingBuses) > 0:
            print("Found prospective buses: {}".format(matchingBuses))
            busName = "/dev/" + matchingBuses[0]
        return busName

    def _updateTimeOffset(self):
        '''
        Request the current time of the M2
        Compare it to the local machine time
        Set self.timeOffset
        '''
        print("Updating time offset...")
        print("is open: {}".format(self.serial.is_open))
        
        # read the bus till we get a result
        startTime = time.time()
        t = None
        while t == None:
            time.sleep(.1)
            self.serial.write(b'\xf1\x01') # request time
            assert (time.time()-startTime) < 3.0 , "Did not get a response from M2 with time data in {} seconds!".format(time.time()-startTime)
            rawData = self.serial.readall()
            for idx in range(len(rawData)-5): # -5 is for 4 data bytes and 1 data type byte
                if (rawData[idx] == 241) and (rawData[idx+1] == 1): # is a time sync response 0xf1=241 and 0x01=1
                    t = struct.unpack('I',rawData[idx+2:idx+6])[0]/1e6
                    break
        self.timeOffset = time.time()-t
        print("time offset: {}".format(self.timeOffset))

    def _convertCANDataToCANRequestPackets(self):
        '''
        pre process the conversion of self.CANData to the actual packets that need to be sent over serial
        There is no sense in doing this every time we send the data
        Send:
        |  byte range  |  data type  |  Value  |  description
        |      0       |     NA      |   0xf1  |  start of packet
        |      1       |     int     |    -    |  0x00 indicates it is a canbus frame
        |     2-5      |     hex     |    -    |  CAN ID ( 4 bytes)
        |      6       |     int     |   0x00  |  Bus to send on, 0 = CAN0, 1 = CAN1, 2 = SWCAN, 3 = LIN1, 4 = LIN2
        |      7       |     int     |    -    |  length of data
        |     8+       |     NA      |    -    |  data bytes
        '''
        self.CANRequestPackets = []
        for frame in self.CANData:
            packet = b'\xf1\x00'
            packet += frame["id"]
            packet += bytes([len(frame["data"])])
            packet += frame["data"]
            self.CANRequestPackets.append(packet)
            print("created packet: ",end="")
            print(packet)

    def __call__(self):
        '''
        Send out requests for data
        Recieve data from M2
        '''
        # do rate limiting
        currentTime = time.time()
        if currentTime - self.rateLimit > self.lastDataSend:
            print("Sending CAN Packets")
            self.lastDataSend = currentTime
            for packet in self.CANRequestPackets:
                self.serial.write(packet)

        # read in the packets. We are using the ASCII mode with the M2 (never send b'\xe7')
        # We need to check that the first character is not the symbol for the start of a binary packet (b'\xf1')
        # If it is not a binary packet, add to save list, otherwise ignore it
        dataPackets = self.serial.readlines()
        for packet in dataPackets:
            if packet[0] != 241:
                self.parseCANPacket(packet)

        self.saveParsedData()

    def parseCANPacket(self,packet):
        '''
        Add the packet to the list of dicts to write
        '''
        p= packet.decode("utf-8")[:-2]
        p = p.split(" ")
        t = str(float(p[0])/1e6 + self.timeOffset)
        CANid = p[2]
        mode = p[3]
        bus = p[4]
        #length = p[5]
        data = p[6:]

        parsed = "{},{},{},{}".format(t,CANid,mode,bus)
        for d in data:
            parsed += ",{}".format(d)
        self.parsedCANData.append(parsed)

    def saveParsedData(self):
        '''
        self.newOutputFileFrequency = newOutFileFrequency
        self.fileStartedAt = 0 # the time at which the current file was created, set in saveParsedData
        self.fileCount = -1 # t

        save the parsed data
        '''
        with open(self.outputFile,'a') as f:
            for l in self.parsedCANData:
                f.write(l)
                f.write("\n")
        self.parsedCANData = []


