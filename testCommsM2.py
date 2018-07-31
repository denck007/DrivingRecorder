import serial
import time
import os


def _findBus():
    '''
        Attempt to find a bus to connect to
    '''
    allBusNames = os.listdir("/dev/")
    matchingBuses = [x for x in allBusNames if "ttyACM" in x]

    busName = ""
    if len(matchingBuses) > 0:
        print("Found prospective buses: {}".format(matchingBuses))
        busName = "/dev/" + matchingBuses[0]
    return busName

serialBusName = _findBus()
assert serialBusName != "", "No device found at /dev/ttyACM*"


print("Starting serial communication with M2...")
s = serial.Serial(serialBusName,1152000,timeout=0)
time.sleep(1) # Let the M2 boot and dump all its boot info to serial
while True:
    data = s.readlines() # then read it all to clear it
    print(data)


