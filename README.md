# DrivingRecorder
Record data from a CAN bus and cameras using a [Macchina M2](https://www.macchina.cc/), webcam, and Python. This is part of a larger project to build a machine learning dataset, so I am trying to make getting at the underlying data as painless and easy as possible. It is not meant to be run completely headless and unmonitored for a long period of time. For development I am using a 2015 Mazda 3. 

## Requirements:
* Python 3.6, any python 3 should work
* OpenCV 3, I have been using [3.2 from menpo on anaconda](https://anaconda.org/menpo/opencv3)
* numpy
* M2RET, installed on the M2
* SavvyCAN
* Webcam, I have had really good sucess with the Logitech c920 mounted to my rear view mirror
* Serial bus be listed in /dev/ttyACM* This should be the case for must ubuntu type systems. The only thing that requires this is the automatic detection of the M2, which happends in SerialCANBus._initializeM2() and SerialCANBus._findBus() methods. Modifying these methods should make it work on Windows as well. 

## Setup the recorder
There are a lot of settings to play with in the recorder. Right now they are all hardcoded in at the top of DrivingRecorder.py. There should be no need to change things in other files. 

### Settings
printEvery: How often the terminal is updated, acts like a heartbeat so you know it is still alive

outDir: The path where everything is saved to

dataRequestMaxFrequency: How often the script can ask for data from the car. In all reality something like 0.25 seconds is probably reasonable

writeFrequency: How many response packets should be recieved before the are saved to disk. Too low and you will get overhead with contant open and close of the file. Too large and risk loosing data. 1000 is probably reasonable.

captureFrequency: The maximum frequency in Hz that the camera will record. It will likely actually be lower than this value.

camId: the id of the camera to use. If there are multiple cameras attached to the computer you may have to experiment. If you have a built in webcam it is likely a value of 1 will work. If there is only 1 camera attached to the computer than 0 should work.

showImages: True/False, should the captured images be shown? Yes is good for debugging, but it takes overhead to do it

CANData: a dictionary of the CAN packet request ID, response ID, the request packet contents. Note that request id and reponse ID are both least significant bit first! This is the oposite of what SavvyCAN displays and saves to disk. The request data contents are in the same order as displayed/output by SavvyCAN. This has to do with the M2RET software.

### Identifying what data is availible from the car
The easiest way I have found to determine what data is availible from the vehicle is to run an app lik FORscan eusing a bluetooth OBD2 adaptor, and running the M2 at the same time to capture the actual CAN packets using SavvyCAN.

#### Tools
* [FORScan](https://www.forscan.org/download.html)
* [SavvyCAN](https://github.com/collin80/SavvyCAN)
* [OBD2 adaptor with a HS CAN switch or mode](https://www.amazon.com/gp/product/B01MUALTSX/ref=oh_aui_detailpage_o09_s00?ie=UTF8&psc=1) Do not buy the cheapest one out there, they will not work with FORScan.
* [OBD2 splitter](https://www.amazon.com/gp/product/B017IBP1MK/ref=oh_aui_detailpage_o06_s00?ie=UTF8&psc=1) So the M2 and OBD2 adaptor can both be hooked up at the same time
* [Macchina M2](https://www.macchina.cc/catalog) with [M2RET](https://github.com/collin80/M2RET) installed on it
* The linked products are just what I had success with, YMMV.

#### Process
1) Hook up the M2 and OBD2 reader using an OBD2 splitter
2) Set up SavvyCAN to read from the M2. You should see some background communications
3) Identify the parameters that are availible using FORScan and the OBD2 adaptor

4) Stop FORScan
5) Turn on SavvyCAN, filter out the background traffic on the CAN bus. Pause capture.
6) Set FORScan to request 1 parameter from the vehicle, do not start recording yet.
7) At about the same time resume capture in SavvyCAN and start FORscan recording.
8) Interact with the car so that the values in FORscan are changing. It is important to get a large random range of values of the parameters. Record for 10-30 seconds.
9) Export the FORscan data and save the FILTERED SavvyCAN data.
10) Do some reverse engineering of the data packets. See the notebook RE_forscan_vs_savvycan.ipynb for an idea of how I have approched this.
11) Repeat 4-10 for each parameter you would like to record

### Reverse engineering the CAN Packets
Following the steps above, you should have a file from FORscan that has the a single vehicle parameter for a bunch of times, and a file from SavvyCAN that has the CAN packets that were recorded at the same time as the FORscan file. 

Step 1: Determine what the request and responses are

The way the CAN bus works is we ask a particular computer in the car for a specific parameter. It then sends a packet back in response. There should only be 2 ids listed in the SavvyCAN file, the request and the response, and they should be offset by 0x08 (but other offsets are allowed by the standard). IE there if one of the ids is 0x07 0x30 the other one is likely 0x07 0x38. The lower number is the request (0x07 0x30), the higher value is the response (0x07 0x38). This id is for a specific computer (ECU) on the vehicle, all requests and responses with this ID are from the same ECU. The data in the packet specifies what parameter we are looking for. In my case, the first 4 bytes specify what parameter we are talking about, and the last 4 define the value. Between the request and response, only bytes 3 and 4 match. The second byte is usually specifiying what 'bus' the ECU is on, in general the interesting data is on the 0x22 bus and responds with a second data byte of 0x62. The first byte in the response does not match the request, but the offset varies for each parameter. 

For example:

Type | ID | byte 1 | byte 2 | byte 3 | byte 4 | byte 5 | byte 6 | byte 7 | byte 8
-------- | ------------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ 
Request | 0x07 0x30 | 0x03 | 0x22 | 0x33 | 0x02 | 0x00 | 0x00 | 0x00 | 0x00 
Response | 0x07 0x38 | 0x05 | 0x22 | 0x33 | 0x02 | 0x50 | 0x03 | 0x00 | 0x00 

This reads out as: request the parameter 0x33 0x02 from ECU 0x07 0x30 on bus 0x22. The response is 0x02 0x50. 

Step 2: Figure out what the response data actually means

From my experience the easiest thing to do is to plot out the values. Plot the data from FORscan, this will tell you what you are looking for. Then try different conversions of the data bytes and see what works. The [python struct package](https://docs.python.org/3/library/struct.html) makes this pretty easy. Then plot out the the values given by different conversion factors and find the chart shape that matches (the values likely will not). Once the plots look the same, play with the scaling to figure out a formula to convert the data.

Examples of conversions

Number of bytes | [Conversion factor](https://docs.python.org/3/library/struct.html#format-characters) | Formula 
 -------------- | ---------------------- | -------
1 | B | value
1 | B | value/x + 128
1 | - | 0x20 mean no output, 0x21 meant left, 0x22 meant right
2 | h | value
2 | h | value/x + 128
2 | B,B | each byte converted individually, byte5*10+byte6

### Getting the vehicle parameters for each image
The images are all stored by the time they were taken (epoch) down to the milli second. The problem is that data from the CAN bus is likely not at the exact same time as the image was taken. The assumption is made that there is enough data collected that it can be linearly interpolated from one data point to the next.A command line tool, convertCANData.py helps with this:
1) It read in the raw CAN data from the CANData.csv file. It converts the raw data to real values, this means that the conversion function will need to be re-written with the CAN packet ids and data for each vehicle. 
2) Filter out any data that does not have a data point within some specified amount of time (default is 1 second)
3) Filter out the images that do not have a data point within the specified amount of time
4) Interpolate the data for the all the remaining images
5) Export the result to a csv with a row for each image, and columns of time (image name), and vehicle parameters.
