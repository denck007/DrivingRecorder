

import os

sourcePath = "/home/neil/car/DrivingData/2018-06-20T16:52:25"
outputPath = "/home/neil/car/DrivingData/2018-06-20T16:52:25/imgs"
charactersToRemoveFromFront = 4

imgs = [x for x in os.listdir(sourcePath) if "jpeg" in x]
l = len(imgs[0][:imgs[0].find(".")])
print("Found {} files, characters before decimal is {}".format(len(imgs),l))

def milliSecondsToSeconds(path,name):
    extensionIdx = name.rfind(".")
    sourceDecimalIdx = name.find(".")
    newDecimalIdx = sourceDecimalIdx -3
    
    if extensionIdx <=0 or newDecimalIdx <=0: # make sure we found the right values
        print("Error with file {}".format(name))
        return
    elif  sourceDecimalIdx==10: # the source name is already good
        return
    
    newName = name[:newDecimalIdx] + "."
    newName += name[newDecimalIdx:sourceDecimalIdx]
    newName += name[sourceDecimalIdx+1:]
    #print("sourceName: {}".format(name))
    #print("newName:    {}".format(newName))
    #print(newDecimalIdx)
    os.rename(os.path.join(path,name),os.path.join(path,newName))
    return newName

def removeCharactersFromFront(path,name,toRemove):
    '''
    remove the specified number of characters from the front of the file name
    '''
    newName = name[toRemove:]
    os.rename(os.path.join(path,name),os.path.join(path,newName))
    return newName

def changeFolder(sourcePath,newPath,name):
    '''
    move the file from the source folder to the outputFolder
    '''
    os.rename(os.path.join(sourcePath,name),os.path.join(newPath,name))

#run it!
for idx,img  in enumerate(imgs):
    print("idx: {} img: {}".format(idx,img))
    changeFolder(sourcePath,outputPath,img)
    newName = removeCharactersFromFront(outputPath,img,charactersToRemoveFromFront)
    milliSecondsToSeconds(outputPath,newName)