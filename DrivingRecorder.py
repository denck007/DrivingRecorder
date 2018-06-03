
'''
This is meant to generate data for ML training
It will:
 * Send out requests for data from the car over CAN bus (using an M2 connected via serial)
 * Recieve the data back from the CAN bus
 * Filter out unwanted data
 * Save data by the epoch at which it happened, down to the mili-second
 * * The macchina M2 sends time back in micro-seconds
 * Capture a frame from a camera at 5 Hz
'''

from SerialCANBus import SerialCANBus
from RecordWebcam import RecordWebCam
import time
import sys

# Settings:
printEvery = 0.5 # seconds
outputPath = "testRecord/"#
CANDataFile = outputPath + "test.csv"
dataRequestMaxFrequency = 0.1 # seconds
writeFrequency = 1 #number of packets to build up before saving to disk
captureFrequency = 5.0 # Hz
camId = 1
showImages = True
CANData = [{"id":b'\x30\x07\x00\x00',"responseId":b'\x38\x07\x00\x00','data':b'\x03\x22\x33\x02\x00\x00\x00\x00'}]
#CANData= []

# initalize objects:
carData = SerialCANBus(CANDataFile,CANData=CANData,dataRequestMaxFrequency=dataRequestMaxFrequency,writeFrequency=writeFrequency,hexExplicit=False)
imageRecorder = RecordWebCam(outputPath,captureFrequency=captureFrequency,camId=camId,show=showImages)

lastPrint = 0
try:
    while True:
        time.sleep(.01)
        currentTime = time.time()
        if currentTime - printEvery > lastPrint:
            lastPrint = currentTime
            print("\rRecording data at {:.3f}".format(currentTime),end="")
        carData()
        imageRecorder()
except(KeyboardInterrupt,SystemExit):
    print("\nShutting down by user request...")
    carData.saveParsedData()
    imageRecorder.shutDown()
    
    print("Exiting!")
    
    




