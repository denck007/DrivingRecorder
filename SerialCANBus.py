
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
        This is required as the CAN data must be sent back as binary inorder to send out requests

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

    def __init__(self,outputFile,CANData=[],serialBusName="",dataRequestMaxFrequency=0.1,writeFrequency=100):
        '''
            outputFile: the csv file to save data to.
            CANData: list of dicts that define all the packets we are sending
                        [{"id":b'<4 byte CAN id as bytes>',"responseId":<b'<4 byte CAN id as bytes>',"data":<bytes to request>}]
            serialBus: The bus that the M2 is attached to. If nothing is provided it will attempt to connect to the first bus
                        listed in /dev/ttyACM*
            dataRequestMaxFrequency: the minimum time between requests for data are sent out in seconds
                        Note that this is a MINIMUM value and it is likely to take longer
            writeFrequency: The number of responses to be built up before the data is saved to disk, integer
        '''        
        # inorder to not completely spam the CAN bus, we want to rate limit the requests for data
        # this is the time in seconds that must pass between each data send
        self.rateLimit = dataRequestMaxFrequency

        # How many responses must be accumulated before the data is saved
        self.writeFrequency = writeFrequency

        self.lastDataSend = 0 # record the last time.time() we requested data

        self.outputFile = outputFile
        self.CANData = CANData
        self.serialBusName = serialBusName

        self.data = b''
        self.parsedCANData = []

        self._convertCANDataToCANRequestPackets()
        self._convertCANDataToResponseFilters()
        self._initializeM2() # create self.serial, set timeOffset

        # make sure the output directory exists
        fileDir = outputFile[:outputFile.rfind("/")]
        if not os.path.isdir(fileDir):
            os.makedirs(fileDir)

        print("Finished setting up CAN Recorder!")

    def _initializeM2(self):
        '''
        initialize the M2
        '''
        if self.serialBusName == "":
            self.serialBusName = self._findBus()
        assert self.serialBusName != "", "No device found at /dev/ttyACM*"

        print("Starting serial communication with M2...")
        self.serial = serial.Serial(self.serialBusName,1152000,timeout=0)
        self.serial.write(b'\xe7') # tell M2RET to respond in binary
        time.sleep(2) # Let the M2 boot and dump all its boot info to serial
        self.serial.read_all() # then read it all to clear it

        self._updateTimeOffset()

    def _findBus(self):
        '''
            Attempt to find a bus to connect to
        '''
        allBusNames = os.listdir("/dev/")
        matchingBuses = [x for x in allBusNames if "ttyACM" in x]
        
        busName = ""
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
        print("Updated time offset: {}".format(self.timeOffset))

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

    def _convertCANDataToResponseFilters(self):
        '''
        We do not want to save all of the data on the bus, only the responses to what we have asked for.
        Responses come in with ID of sendId + returnDataOffset
        Make a list of strings that match the responses so they can be quickly filtered later
        '''
        self.CANResponseFilters = []
        for frame in self.CANData:
            responseId = frame["responseId"]
            data = "0x"
            for byte in responseId:
                d = "{:02x}".format(byte)
                data += ("{}".format(d.zfill(2)))
            self.CANResponseFilters.append(data)

    def __call__(self):
        '''
        Send out requests for data
        Recieve data from M2
        '''
        # do rate limiting
        currentTime = time.time()
        if currentTime - self.rateLimit > self.lastDataSend:
            self.lastDataSend = currentTime
            for packet in self.CANRequestPackets:
                self.serial.write(packet)

        # read in the packets
        self.data += self.serial.read_all()
        idx = 0
        dataLength = len(self.data)
        while idx < dataLength:
            # 241==0xf1 start of packet and 0==0x00 can packet
            if self.data[idx] == 241 and self.data[idx+1] == 0:
                idx = self._parseCANPacket(idx)
            else:
                idx += 1
        self.data = self.data[idx:]

        # cut down write frequency
        if len(self.parsedCANData) > 100:
            self.saveParsedData()

    def _parseCANPacket(self,idx):
        '''
        parse the CAN packet that starts at idx
        '''
        if idx+11>len(self.data): # the can frame length is not included, so escape
            return idx

        t = struct.unpack('I',self.data[idx+2:idx+6])[0]/1e6 + self.timeOffset
        # parse out the CAN Id
        CANId = "0x"
        for byte in self.data[idx+6:idx+10]:
            d = "{:02x}".format(byte)
            CANId += ("{}".format(d.zfill(2)))

        # get the data from the CAN frame. 
        d = []
        messageLength = self.data[idx+10]
        endOfMessageIdx = idx + 11 + messageLength
        #If the frame is not one we asked for then skip the entire thing
        if CANId not in self.CANResponseFilters:
            return endOfMessageIdx
        #the data is not included so skip for now
        elif endOfMessageIdx > len(self.data):
            return endOfMessageIdx

        for ii in range(11,11+messageLength-1):
            d.append(hex(self.data[idx+ii]))
        self.parsedCANData.append({'time':t,'canId':CANId,'data':d})
        return endOfMessageIdx

    def saveParsedData(self):
        '''
        save the parsed data
        If the data is there, it then we asked for the data and we should save it
        '''
        with open(self.outputFile,'a') as f:
            for packet in self.parsedCANData:
                f.write("{},{},".format(packet["time"],packet["canId"]))
                for b in packet["data"]:
                    d = "{}".format(b)[2:]
                    f.write("0x{},".format(d.zfill(2)))# make every one the same size
                f.write("\n")
        self.parsedCANData = []

