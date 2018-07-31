// Arduino Due - Displays all traffic found on either canbus port
// By Thibaut Viard/Wilfredo Molina/Collin Kidder 2013-2014

// Required libraries
#include "variant.h"
#include <due_can.h>

//Leave defined if you use native port, comment if using programming port
//This sketch could provide a lot of traffic so it might be best to use the
//native port
#define Serial SerialUSB


const int numFrames = 14; // number of rames we are sending
CAN_FRAME framesToSend[numFrames];
int timeBetweenRequests = 500;

int lastSend = 0;



/*
int readIntFromSerial() {
  const char maxNumChars = 255;
  byte data[maxNumChars];
  uint8_t idx = 0;
  while (Serial.available() == 0) {} // wait for input
  while (Serial.available() && data[idx - 1] != '\n') { // read all the input
    if (idx > maxNumChars) {
      break;
    }
    data[idx] = Serial.read();
    idx += 1;
  }
  data[idx] = 0; // end in null
  //String str((char*)data);Serial.print("You entered ");Serial.print((char*)data);Serial.print("\n"); // debugging
  return String((char*)data).toInt();
}

byte readByteFromSerial() {
  while (Serial.available() == 0) {} // wait for input
  return Serial.read();
}

*/

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(200);
  while (!Serial) {
    ; // wait for serial port to connect before continuing
  }
  Serial.print("Starting M2\n");

  int idx = 0; 
  // SteeringWheelAngle
  framesToSend[idx].id = 0x730;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x33;
  framesToSend[idx].data.bytes[3] = 0x02;

  // SteeringWheelSpeed
  
  framesToSend[idx].id = 0x730;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x33;
  framesToSend[idx].data.bytes[3] = 0x01;

  // SteeringWheelTorque
  idx +=1; 
  framesToSend[idx].id = 0x730;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x33;
  framesToSend[idx].data.bytes[3] = 0x0B;
  
  // turnSignal
  idx +=1; 
  framesToSend[idx].id = 0x731;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0xD9;
  framesToSend[idx].data.bytes[3] = 0x80;

  // acceleratorPosition
  idx +=1; 
  framesToSend[idx].id = 0x7E0;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x03;
  framesToSend[idx].data.bytes[3] = 0x0B;

  // clutchPosition
  idx +=1; 
  framesToSend[idx].id = 0x7E0;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x07;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x1E;
  framesToSend[idx].data.bytes[3] = 0x04;
  
  // brakePressure
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x05;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x20;
  framesToSend[idx].data.bytes[3] = 0x34;
    
  // vehicleSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x04;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0xF4;
  framesToSend[idx].data.bytes[3] = 0x0D;
    
  // leftFronWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x04;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x06;
      
  // rightFronWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x04;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x07;
      
  // leftRearWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x04;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x08;
      
  // rightRearWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x04;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x09;
      
  // longitudinalAcceleration
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x05;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x11;
      
  // lateralAcceleration
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x04;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x0C;
  /*
  // get the loop frequency which controls how often the data is requested
  // also get the number of can frames we will be sending each loop
  // frequency is in Hz, so an uint8_t will get us 0.004seconds to 1 second between data collection
  //    which should be sufficient
  // the number of can frames is also a uint8_t which implies a limit of 255 frames that can be asked for
  byte data[255*12+2]; // allocate enough space to send 255 12byte frames(8 data + 3 id + 1 length) + 2 for the timing and number of frames
  Serial.print("Enter request frequency and number of frames\n");
  while (Serial.available() == 0) {} // wait for input
  Serial.readBytes(data,255*12+2);
  timeBetweenRequests = int(1.0 / float(data[0]) * 1000.0);
  numFrames = int(data[1]);
  Serial.print("Time between requests is ");Serial.print(timeBetweenRequests); Serial.print(" milliseconds\n");//debug
  Serial.print("Going to send ");Serial.print(numFrames); Serial.print(" frames\n");//debug
  int idx;
  uint32_t id;
  char frameData[8];
  uint8_t len;
  for(idx=2;idx<numFrames;0){
    len = uint8_t(data[idx]);
    idx += 1;
    id = data[idx]; idx+=1;
    id = data[idx] << 8; idx+=1;
    id = data[idx] << 16; idx+=1;
    for(uint8_t l = 0; l<len;l++){
      
    }
  }

  // set the frequency at which the loop() function runs
  // This controls how often we ask the car for data
  //Serial.print("milliseconds between packet requests:\n");
  //requestFrequency = readIntFromSerial();

  // get the total number of CAN frames we are going to work with
  //Serial.print("number of CAN frames:\n");
  //numFrames = readByteFromSerial();
  //Serial.print("Going to read "); Serial.print(numFrames, DEC); Serial.print(" frames from serial\n"); // debugging



  // read in each CAN frame
  // everything is in bytes
  //
  const byte maxNumChars = 255;
  for (int idx = 0; idx < numFrames; idx++) {
    byte data[maxNumChars];
    idx = 0;
    while (Serial.available() == 0) {} // wait for input
    while (Serial.available()) { // read all the input
      if (idx > maxNumChars) {
        break;
      }
      data[idx] = Serial.read();
      idx += 1;
    }
  }





  //const char maxNumChars = 50;
  //uint8_t data[maxNumChars];
  //char idx = 0;
  //while(Serial.available()==0){}// wait for input
  //    while(Serial.available()){ // read all the input
  //      if (idx>maxNumChars){break;}
  //      data[idx] = Serial.read();
  //      idx += 1;
  //}
  //data[idx] = 0; // end in null
  //String str((char*)data);Serial.print("You entered ");Serial.print((char*)data);Serial.print("\r\n"); // debugging
  //requestFrequency = String((char*)data).toInt();

*/



  Can0.begin(CAN_BPS_500K);


  //By default there are 7 mailboxes for each device that are RX boxes
  //This sets each mailbox to have an open filter that will accept extended
  //or standard frames
  int filter;
  //extendeds
  for (filter = 0; filter < 3; filter++) {
    Can0.setRXFilter(filter, 0, 0, true);
    Can1.setRXFilter(filter, 0, 0, true);
  }
  //standard
  for (int filter = 3; filter < 7; filter++) {
    Can0.setRXFilter(filter, 0, 0, false);
    Can1.setRXFilter(filter, 0, 0, false);
  }

  //delay(5000);

  pinMode(DS2, OUTPUT);
  digitalWrite(DS2, LOW);

  Serial.print("Setting RX filter\n");
  int filterStatus;
  filterStatus = Can0.setRXFilter(0, 0x738, 0xffffff, false);
  filterStatus = Can0.setRXFilter(1, 0x739, 0xffffff, false);
  filterStatus = Can0.setRXFilter(2, 0x7E8, 0xffffff, false);
  filterStatus = Can0.setRXFilter(3, 0x768, 0xffffff, false);
  Can0.setCallback(0,writeFrameToSerial);
  Can0.setCallback(1,writeFrameToSerial);
  Can0.setCallback(2,writeFrameToSerial);
  Can0.setCallback(3,writeFrameToSerial);
  
  if (filterStatus >= 0) {
    Serial.print("Set RX filter on mailbox ");
    Serial.print(filterStatus);
  } else {
    Serial.print("Failed to set RX filter on mailbox");
    Serial.print(filterStatus);
  }
  
  Serial.print("\n");
}

void writeFrameToSerial(CAN_FRAME *frame) {
  digitalWrite(DS6, !digitalRead(DS6)); // invert status of green led
  Serial.print(millis());
  Serial.print(" ID: 0x");
  Serial.print(frame->id, HEX);
  Serial.print(" Len: ");
  Serial.print(frame->length);
  Serial.print(" Data: 0x");
  for (int count = 0; count < frame->length; count++) {
    Serial.print(frame->data.bytes[count], HEX);
    Serial.print(" ");
  }
  Serial.print("\r\n");
}

void sendFrame() {
  CAN_FRAME myFrame;
  myFrame.id = 0x730;
  myFrame.extended = false;
  myFrame.length = 8;
  myFrame.data.bytes[0] = 0x03;
  myFrame.data.bytes[1] = 0x22;
  myFrame.data.bytes[2] = 0x33;
  myFrame.data.bytes[3] = 0x02;
}

void loop() {
  CAN_FRAME incoming;

  if (lastSend+timeBetweenRequests >= millis()){
    digitalWrite(DS5, !digitalRead(DS5)); // invert status of first yellow LED
    for (int ii=0;ii<numFrames;ii++){
      Can0.sendFrame(framesToSend[ii]);
    }
  }
  //delay(100);
  //Serial.print(millis());
  //Serial.print("\r\n");

}


