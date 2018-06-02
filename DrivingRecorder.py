
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
captureFrequency = 5.0 # Hz
camId = 1
#CANData = [{"id":b'\x00\x00\x07\x30','data':b'\x03\x22\xd9\x00\x00\x00\x00\x00'}]
CANData= []

# initalize objects:
carData = SerialCANBus(CANDataFile,CANData=CANData)
imageRecorder = RecordWebCam(outputPath,captureFrequency=captureFrequency,camId=camId)

lastPrint = 0
try:
    while True:
        currentTime = time.time()
        if currentTime - printEvery > lastPrint:
            lastPrint = currentTime
            print("\rRecording data at {:.3f}".format(currentTime),end="")
        carData()
        imageRecorder()
except(KeyboardInterrupt,SystemExit):
    print("\nShutting down by user request...")
    imageRecorder.cap.release()
    print("Exiting!")
    
    




