'''
For use in recording a usb camera mounted in a car
'''
import os
import time
import cv2

class RecordWebCam(object):

    def __init__(self,outPath,captureFrequency=5.0,camId=0):
        '''
        outPath: path where the images are to be stored
            Images will be stored as <epoch in milliseconds>.jpeg
        captureFrequency: the frequency in hertz to save a frame
        camId: the index of the usb camera to use, defaults to 1 but may need to change for multi camera machines
        '''
        self.outPath = outPath
        self._checkOutPath()
        self.timeBetweenFrames = 1.0/captureFrequency

        self.lastCapture = 0

        # create the video stream
        self.camId = camId
        self.cap = cv2.VideoCapture(camId)

        print("Finished setting up camera {}!".format(self.camId))

    def _checkOutPath(self):
        '''
        Verify that self.outPath is a directory
        '''

        if self.outPath[-1] != "/":
            self.outPath += "/"
        self.outPath += "imgs/"

        if not os.path.isdir(self.outPath):
            os.makedirs(self.outPath)


    def __call__(self):
        '''
        when called cature and save a frame
        '''
        currentTime = time.time()       
        if currentTime - self.timeBetweenFrames > self.lastCapture:
            self.lastCapture = currentTime
            ret,frame = self.cap.read()
            assert ret, "Lost connection with camera {}!".format(self.camId)
            frame = cv2.flip(frame,-1)
            cv2.imwrite("{}{:0f}.jpeg".format(self.outPath,currentTime*1000),frame)