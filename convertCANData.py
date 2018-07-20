# convert CANData.csv files to data files
# need to convert the raw CAN packets to useful information
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
            row.output = struct.unpack("h",d6+d5)[0]/30
            row.commonName = "steeringWheelAngle"
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\x33' and d4 == b'\x0b':
            # steering torque
            row.commonName = "steeringWheelTorque"
            row.output = (struct.unpack("B",d5)[0]-127)/10
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\x33' and d4 == b'\x01':
            # steering torque
            row.commonName = "steeringRotationSpeed-NOTIMPLEMENTED"
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
            elif d5 == b'\x22':
                row.output = 1
            else:
                print("Unknown value for turn signal: {}".format(row))
        else:
            print("Unknown packet from cluster: {}".format(row))
    elif row["ID"] == '000007e8': #
        if d1 == b'\x04' and d2 == b'\x62' and d3 == b'\x03' and d4 == b'\x2b':
            # accelerator position, 0-100%
            row.output = struct.unpack("B",d5)[0]
            row.commonName = "acceleratorPosition"
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\xf4' and d4 == b'\x0d':
            # vehicleSpeed in kph
            row.output = struct.unpack("B",d5)[0]
            row.commonName = "vehicleSpeed"
        elif d1 == b'\x04' and d2 == b'\x62' and d3 == b'\xf4' and d4 == b'\x45':
            # throttle position 0-1
            row.output = struct.unpack("B",d5)[0]/255
            row.commonName = "throttlePosition"
        else:
            print("Unknown packet from PCM? : {}".format(row))
    elif row["ID"] == '00000768': # ABS module
        if d1 == b'\x05' and d2 == b'\x62' and d3 == b'\x2b' and d4 == b'\x0d':
            # brake pressure
            row.commonName = "brakePressure?-NOTIMPLEMENTED"
        else:
            print("Unknown packet from ABS : {}".format(row))
    else:
            print("Unknown packet: {}".format(row))

    return row
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert a csv of captured CAN packets to individual csv files of just the data and time")
    parser.add_argument("inputFile",help="inputFile")

    args = parser.parse_args()

    inputFile = args.inputFile#"/home/neil/car/DrivingData/2018-06-10T13:32:29/CANData.csv"
    outputFilesPath = inputFile[:inputFile.rfind("/")]
    assert os.path.isfile(inputFile), "The input file does not exist!"

    dtype = {"TimeStamp":float, "ID":bytes, "d1":bytes, "d2":bytes, "d3":bytes,"d4":bytes, "d5":bytes, "d6":bytes, "d7":bytes, "d8":bytes,"dummy":str}
    data = pd.read_csv(inputFile,index_col=False,dtype=dtype)
    data.columns = ["TimeStamp","ID","d1","d2","d3","d4","d5","d6","d7","d8","dummy"]

    data["output"] = 0
    data["commonName"] = ""
    data = data.apply(lambda row: convertRow(row),axis=1)

    # get unique names
    names = list(set(data.commonName.tolist()))
    colsToWrite = ["TimeStamp","output"]
    for n in names:
        outName = os.path.join(outputFilesPath,n+".csv")
        if "NOTIMPLEMENTED" in outName: # skip outputing not implemented data
            continue
        data[data.commonName==n].to_csv(outName,float_format="%.3f",columns=colsToWrite,index=False)

