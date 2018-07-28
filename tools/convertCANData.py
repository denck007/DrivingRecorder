# Tool to read in image times and the CANData.csv file and out the interpolated value for each
#   car parameter at the time of the image.

import pandas as pd
import numpy as np
import struct
import os
import argparse

def convertToBytes(x):
    if len(x) == 1:
        x = "0" + x
    out = bytes.fromhex(x)
    return out
def convertRow(row):
    def convertToByte(x):
        if len(x) == 1:
            x = "0" + x
        out = bytes.fromhex(x)
        return out

    d1 = convertToByte(row.d1)
    d2 = convertToByte(row.d2)
    d3 = convertToByte(row.d3)
    d4 = convertToByte(row.d4)
    d5 = convertToByte(row.d5)
    d6 = convertToByte(row.d6)
    d7 = convertToByte(row.d7)
    d8 = convertToByte(row.d8)
    
    if row["ID"] == '00000738': #EPS unit
        if d1 == b'\x05' and d2 == b'\x62' and d3 == b'\x33' and d4 == b'\x02':
            # steering wheel angle, relative to vehicle start
            row.output = struct.unpack("h",d6+d5)[0]/10-780
            row.commonName = "steeringWheelAngle"
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\x33' and d4 == b'\x0b':
            # steering torque
            row.commonName = "steeringWheelTorque"
            row.output = (struct.unpack("B",d5)[0]-127)/10
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\x33' and d4 == b'\x01':
            # steering rotation speed
            row.commonName = "steeringRotationSpeed"
            row.output = struct.unpack("B",d5)[0]*4
        else:
            print("Unknown packet from EPS: {}".format(row))
            
    elif row["ID"] =='00000739': # 
        if d1 == b'\x05' and d2 == b'\x62' and d3 == b'\xd9' and d4 == b'\x80':
            #turn signal indicator
            row.commonName = "turnSignal"
            if d5 == b'\x20': # none
                row.output = 0
            elif d5 == b'\x21': # left
                row.output = -1
            elif d5 == b'\x22': # right
                row.output = 1
            else:
                print("Unknown value for turn signal: {}".format(row))
        else:
            print("Unknown packet from cluster: {}".format(row))

    elif row["ID"] == '000007e8': # PCM
        if d1 == b'\x04' and d2 == b'\x62' and d3 == b'\x03' and d4 == b'\x2b':
            # accelerator position, 0-100%
            row.output = struct.unpack("B",d5)[0]/2
            row.commonName = "acceleratorPosition"
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\xf4' and d4 == b'\x0d':
            # vehicleSpeed in kph
            row.output = struct.unpack("h",d6 + d5)[0]/255
            row.commonName = "vehicleSpeed"
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\xf4' and d4 == b'\x45':
            # throttle position 0-1
            row.output = struct.unpack("B",d5)[0]/255
            row.commonName = "throttlePosition"
        else:
            print("Unknown packet from PCM? : {}".format(row))
    elif row["ID"] == '00000768': # ABS module
        if d1 == b'\x05' and d2 == b'\x62' and d3 == b'\x20' and d4 == b'\x34':
            # brake pressure
            row.output = struct.unpack("h",d6 + d5)[0]*33.3
            row.commonName = "brakePressure"
        else:
            print("Unknown packet from ABS : {}".format(row))
    else:
            print("Unknown packet: {}".format(row))

    return row
    
def GetImageTimes(path,extension="jpeg"):
    '''
    Given a path and extension(default=jpeg), get all the files in the path that match the extension
    Return a list of times
    This assumes that file names are decimal times in seconds
    '''
    assert os.path.exists(path), "Provided path does not exist!\n{}".format(path)
    imgs = [x for x in os.listdir(path) if extension in x]
    assert len(imgs) > 2, "There must be at least 2 images of type {} in the path {}".format(extension,path)    
    
    extensionLength = len(extension)+1
    times = [float(t[:-extensionLength]) for t in imgs]
    return np.sort(np.array(times))

def FilterDataByDelta(data,maxDelta=1.0):
    '''
    Takes in a data frame with the columns: TimeStamp and output
    Returns a dataframe with columns: TimeStamp and output that has 1 less row the the source dataframe
    Filters the data frame so that any output row that does not have an output in the 
        next maxDeta seconds is removed
    '''
    ts = np.array(data.TimeStamp[:-1])
    ts2 = np.array(data.TimeStamp[1:])
    data = data[:-1] # remove last data point
    data = data.assign(delta = ts-ts2)
    data = data[data.delta<maxDelta] # filter out deltas that are too big
    data = data.reset_index() # need to reset the indices as there are gaps now
    data = data.drop(labels="delta",axis=1) # get rid of delta column
    return data

def FilterImgTimesByDataTimes(imgTimes,dataTimes,maxDelta=1.0):
    '''
    Given np arrays of image times and data times, 
        filter the image times so that there is always a data point within maxDelta of the image
    1) get 1D array of times of images, imgTimes
    2) get 1D array of times of samples, dataTimes
    3) IMGTimes,DATATimes = np.meshgrid(imgTimes,dataTimes)
    4) locs = np.where(np.abs(IMGTimes-DATATimes)<=maxDelta)
    * The result in locs is (idx of dataTimes, idx of imgTimes)
    5) imgLocs = np.unique(locs[1])
    6) imgTimes = imgTimes[imgLocs]
    '''
    IMGTimes,DATATimes = np.meshgrid(imgTimes,dataTimes)
    locs = np.where(np.abs(IMGTimes-DATATimes)<maxDelta)
    imgLocs = np.unique(locs[1])
    return imgTimes[imgLocs]

if __name__ == "__main__":

    knownBadFormats = ["throttlePosition","turnSignal","vehicleSpeed","steeringWheelTorque","acceleratorPosition"]

    parser = argparse.ArgumentParser(description="Convert a csv of captured CAN packets to individual csv files of just the data and time")
    parser.add_argument("inputPath",help="Path with CANData.csv and folder imgs/ with all the images in it")
    parser.add_argument("--maxDelta",help="The maximum difference in time between an image and data points",default=1.0)
    parser.add_argument("--outputFile",help="The output csv file",default="interpolatedData.csv")
    args = parser.parse_args()

    inputPath = args.inputPath
    assert os.path.isdir(inputPath), "The specified path does not exist!\n{}".format(inputPath)
    maxDelta = args.maxDelta

    inputCSV = os.path.join(inputPath,"CANData.csv")
    imgPath = os.path.join(inputPath,"imgs")
    assert os.path.isfile(inputCSV), "CANData.csv does not exist in the provided path!"
    assert os.path.isdir(imgPath), "There is no imgs folder in the path!"
    outputCSV = args.outputFile
    if not outputCSV.endswith(".csv"):
        outputCSV = outputCSV + ".csv"
    outputCSV = os.path.join(inputPath,outputCSV)

    imageTimes = GetImageTimes(imgPath)
    print("Found {} images".format(len(imageTimes))) 

    # read in the raw CANData.csv file and convert the bytes to real values
    dtype = {"TimeStamp":float, "ID":bytes, "d1":bytes, "d2":bytes, "d3":bytes,"d4":bytes, "d5":bytes, "d6":bytes, "d7":bytes, "d8":bytes,"dummy":str}
    data = pd.read_csv(inputCSV,index_col=False,dtype=dtype)
    data.columns = ["TimeStamp","ID","d1","d2","d3","d4","d5","d6","d7","d8"]
    data["output"] = 0
    data["commonName"] = ""
    data = data.apply(lambda row: convertRow(row),axis=1)

    # For each type of data, filter out times that do not have another data point within maxDelta seconds
    dataNames = list(set(data.commonName.tolist()))
    for dataName in dataNames:
        if ("NOTIMPLEMENTED" in dataName) or (dataName in knownBadFormats):
            print("Skipping {}".format(dataName))
            continue
        d = data[data.commonName == dataName]
        d = d.sort_values("TimeStamp")
        d = FilterDataByDelta(d,maxDelta=maxDelta)
        dataTimes = np.array(d.TimeStamp)
        imageTimes = FilterImgTimesByDataTimes(imageTimes,dataTimes,maxDelta=maxDelta)
        print("After filtering with {}, now have {} images".format(dataName,len(imageTimes)))
    print("Finished filtering image times based on data\n")

    # now get the values at each imageTime
    interpolatedData = pd.DataFrame(imageTimes,columns=["TimeStamp"])
    interpolatedData = interpolatedData.sort_values("TimeStamp")
    for dataName in dataNames:
        if ("NOTIMPLEMENTED" in dataName) or (dataName in knownBadFormats):
            continue
        print("Interpolating {}...".format(dataName))
        d = data[data.commonName == dataName]
        d = d.sort_values("TimeStamp")
        rawX = np.array(d.TimeStamp)
        rawY = np.array(d.output)
        interpolatedData[dataName] = np.interp(imageTimes,rawX,rawY)
    print("\nSaving data!")
    interpolatedData.to_csv(outputCSV,index=False)

    print("Data was interpolated for {} images with at least 1 point within {:.3f} seconds".format(imageTimes.shape[0],maxDelta))
    print("The file is saved at {}".format(outputCSV))
