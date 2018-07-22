# DrivingRecorder
Record data from car's CAN bus, and from cameras using [Macchina M2](https://www.macchina.cc/) and Python. My goal with this is to create a dataset for machine learning applications. That being said, I am not really reverse engineering that much and have taken steps to make getting at the underlying data as painlessly as possible.

These are tools to record from a web camera and a Macchina M2 using python.
The M2 is running [M2RET](https://github.com/collin80/M2RET).

## Requirements:
* Python 3.6, any python 3 should work
* OpenCV 3, I have been using [3.2 from menpo on anaconda](https://anaconda.org/menpo/opencv3)
* numpy
* M2RET, installed on the M2
* SavvyCAN
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
The easiest way I have found to determine what data is availible from the vehicle is to run an app like [FORScan](https://www.forscan.org/download.html) using a [decent bluetooth OBD2 adaptor](https://www.amazon.com/gp/product/B01MUALTSX/ref=oh_aui_detailpage_o09_s00?ie=UTF8&psc=1) (do not cheap out you need one that is HS CAN capable), and running the M2 at the same time to capture the actual CAN packets using [SavvyCAN](https://github.com/collin80/SavvyCAN. This will require a [OBD2 splitter](https://www.amazon.com/gp/product/B017IBP1MK/ref=oh_aui_detailpage_o06_s00?ie=UTF8&psc=1). The linked products are just the products I had sucess with, YMMV.

This may sound complicated but it is straight forword:
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

### Getting the vehicle parameters for each image
The images are all stored by the time they were taken (epoch) down to the milli second. The problem is that data from the CAN bus is likely not at the exact same time as the image was taken. The assumption is made that there is enough data collected that it can be linearly interpolated from one data point to the next.A command line tool, convertCANData.py helps with this:
1) It read in the raw CAN data from the CANData.csv file. It converts the raw data to real values, this means that the conversion function will need to be re-written with the CAN packet ids and data for each vehicle. 
2) Filter out any data that does not have a data point within some specified amount of time (default is 1 second)
3) Filter out the images that do not have a data point within the specified amount of time
4) Interpolate the data for the all the remaining images
5) Export the result to a csv with a row for each image, and columns of time (image name), and vehicle parameters.





