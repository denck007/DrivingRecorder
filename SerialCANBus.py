import os
import time
import serial


class SerialCANBus(object):

    def __init__(self, outputFile,):
        self.serialBusName = ""
        self._initializeM2() # create self.serial, set timeOffset

        # make sure the output directory exists
        self.outputFile = outputFile
        fileDir = outputFile[:outputFile.rfind("/")]
        if not os.path.isdir(fileDir):
            os.makedirs(fileDir)
        with open(outputFile,'w') as f:
            f.write("TimeStamp,ID,length,d1,d2,d3,d4,d5,d6,d7,d8\n")

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
        #self.serial.write(b'\xe7') # tell M2RET to respond in binary
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
        print("Getting current time from M2 in a really hacky way")
        self.serial.flush()
        self.serial.write(b"\x00")
        #time.sleep(1)
        t = self.serial.read_all()
        print("time: {}".format(t))
        t = float(t)/1000.
        self.timeOffset = time.time()-t
        print("Updated time offset: {} seconds".format(self.timeOffset))

    def __call__(self):
        data = self.serial.read_all()
        if len(data) > 1:
            print("{:.3f}".format(time.time()))
            data = str(data)[2:-1]
            data =  [d for d in data.split("\\n")]
            data = data[:-1]
            with open(self.outputFile,'a') as f:
                for dataLine in data:
                    tEnd = dataLine.find(",")
                    t = float(dataLine[:tEnd])/1000. + self.timeOffset
                    f.write("{:.3f}{}\n".format(t,dataLine[tEnd:]))

            print(data)


#outputFile = "/home/neil/car/DrivingRecorder/test.csv"
#canBus = SerialCANBus(outputFile)
#for ii in range(5):
##    time.sleep(1)
#    canBus()