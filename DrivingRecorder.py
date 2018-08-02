
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
import datetime
import sys
import os

# Settings:
printEvery = 0.5 # seconds
outDir = "/home/neil/car/DrivingData/"
dateString = datetime.datetime.now().replace(microsecond=0).isoformat()
CANDataFile = os.path.join(outDir,dateString,"CANData.csv")
imageDir = os.path.join(outDir,dateString,"imgs")
captureFrequency = 5.0 # Hz
camId = 1
showImages = True

# initalize objects:
carData = SerialCANBus(CANDataFile)
imageRecorder = RecordWebCam(imageDir,captureFrequency=captureFrequency,camId=camId,show=showImages)

lastPrint = 0
startTime = time.time()
try:
    while True:
        time.sleep(.02)
        currentTime = time.time()
        if currentTime - printEvery > lastPrint:
            lastPrint = currentTime
            print("\rRecording data at {:.3f}  Elapsed Time: {:.1f} minutes".format(currentTime,(currentTime-startTime)/60),end="")
        carData()
        imageRecorder()
except(KeyboardInterrupt,SystemExit):
    print("\nShutting down by user request...")
    imageRecorder.shutDown()
    print("Exiting!")
    
    




