
from SerialCANBus import SerialCANBus
import time
import random

# Settings:
outputPath = "testRecord/"#
CANDataFile = outputPath + "test.csv"
CANData = [{"id":b'\x00\x00\x07\x30',"responseId":b'\x00\x00\x07\x38','data':b'\x03\x22\xd9\x00\x00\x00\x00\x00'}]
#CANData= []

# initalize objects:
carData = SerialCANBus(CANDataFile,CANData=CANData)


data_echo_bad = b'\xf1' # start of data
data_echo_bad += b'\x0b' # indicate echo can packet
data_echo_bad += b'\xa0\xb0\xc0\xd0' #frame id
data_echo_bad += b'\x00' # which bus
data_echo_bad += b'\x08' # frame length
data_echo_bad += b'\x10\x11\x12\x13\x14\x15\x16\x1a'

data_echo_good = b'\xf1' # start of data
data_echo_good += b'\x0b' # indicate echo can packet
data_echo_good += b'\x00\x00\x07\x38' #frame id
data_echo_good += b'\x00' # which bus
data_echo_good += b'\x08' # frame length
data_echo_good += b'\x10\x11\x12\x13\x14\x15\x16\x1a'


carData.serial.write(b'\xe7') # set M2RET to respond with binary messages
counter = 0
goodCount = 0
badCount = 0
for count in range(5):#swhile True:
    counter+=1
    print("good: {} bad: {}".format(goodCount,badCount))
    time.sleep(0.1)
    if random.randint(0,1) == 1:
        carData.serial.write(data_echo_good)
        goodCount += 1
    else:
        carData.serial.write(data_echo_bad)
        badCount += 1
    #if random.randint(0,1) >= 1:
    #    for ii in range(random.randint(-2,2)):
    #        carData.serial.write(data_echo_good)
    #        goodCount += 1
    #else:
    ##    for ii in range(random.randint(-2,2)):
     #       carData.serial.write(data_echo_bad)
     #       badCount += 1

    carData()
    
print("good: {} bad: {}".format(goodCount,badCount))
startTime = time.time()
while startTime + 3 > time.time():
    print(time.time())
    time.sleep(1)
    carData()