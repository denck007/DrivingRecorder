
# Some of the original CANData files were saved with an extra comma at the end. Want to remove this so all files are the same.
import os
import argparse

rootpath = "/home/neil/car/DrivingData/"

foldersToRunOn = ["2018-06-10T13:32:29",
                    "2018-06-12T09:54:41",
                    "2018-06-12T18:05:28",
                    "2018-06-12T18:07:39",
                    "2018-06-12T18:22:07",
                    "2018-06-12T20:04:37",
                    "2018-06-20T15:43:24",
                    "2018-06-20T16:38:15",
                    "2018-06-20T16:52:25",
                    "20180603"]

def cleanFile(originalFile):
    path = originalFile[:originalFile.rfind("/")]
    cleanedFile = os.path.join(path,"_CANData.csv")

    with open(originalFile,'r') as o:
        original = o.readlines()
    with open(cleanedFile,'w') as c:
        for idx,line in enumerate(original):
            if idx == 0:
                c.write(line[:line.rfind(",")]+"\n")
            if line.endswith(",\n"):
                c.write(line[:-2]+"\n")
            
    os.rename(os.path.join(path,originalFile),os.path.join(path,"CANData_original.csv"))
    os.rename(os.path.join(path,cleanedFile),os.path.join(path,"CANData.csv"))

for folderName in foldersToRunOn:
    folder = os.path.join(rootpath,folderName)
    f = os.path.join(folder,"CANData.csv")
    cleanFile(f)

