

'''
Given a series of images and an interpolated CANData file, make a video
'''

import cv2
import pandas as pd
import numpy as np
import os
import argparse
import time


if __name__ == "__main__":

    params = ["vehicleSpeed","steeringWheelAngle","steeringWheelTorque","lateralAcceleration","longitudinalAcceleration","brakePressure","turnSignal"]

    parser = argparse.ArgumentParser(description="Create a video based on the interpolated CANData and recorded images")
    parser.add_argument("inputPath",help="Path with interpolatedData.csv and folder imgs/ with all the images in it")
    parser.add_argument("--inputData",help="Option to specify a filename other than '''interpolatedData.csv'''",default='interpolatedData.csv')
    parser.add_argument("--outputFile",help="The output csv file",default="out.mp4")
    args = parser.parse_args()

    inputPath = args.inputPath
    assert os.path.isdir(inputPath), "The specified path does not exist!\n{}".format(inputPath)

    inputData = os.path.join(inputPath,args.inputData)
    imgPath = os.path.join(inputPath,"imgs")
    outputFile = os.path.join(inputPath,args.outputFile)
    assert os.path.isfile(inputData), "CANData.csv does not exist in the provided path!"
    assert os.path.isdir(imgPath), "There is no imgs folder in the path!"

    data = pd.read_csv(inputData,dtype=float)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(outputFile,fourcc,5.0,(1280,720))

    textHeight = 25
    font = cv2.FONT_HERSHEY_DUPLEX


    startTime = time.time()
    nRows = len(data)
    for row in data.iterrows():
        if row[0]%50==1:
            remaining = ((time.time()-startTime)/row[0])*(nRows-row[0])
            print("\rOn frame {}/{}, estimated seconds remaining: {:.1f}".format(row[0],nRows,remaining),end="")
        imgTime = row[1]["TimeStamp"]
        imgName = os.path.join(imgPath,"{:.3f}.jpeg".format(imgTime))
        
        img = cv2.imread(imgName)
        if img is None:
            print("File name {} not found".format(imgName))
        idx = textHeight
        for p in params:
            text = '{}: {:.3f}'.format(p,row[1][p])
            cv2.putText(img,text,(10,idx), font, .75,(255,255,255),1,cv2.LINE_AA)
            idx += textHeight
        out.write(img)
    out.release()
    print("")