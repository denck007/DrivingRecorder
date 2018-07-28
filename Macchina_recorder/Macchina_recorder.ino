// Arduino Due - Displays all traffic found on either canbus port
// By Thibaut Viard/Wilfredo Molina/Collin Kidder 2013-2014

// Required libraries
#include "variant.h"
#include <due_can.h>

//Leave defined if you use native port, comment if using programming port
//This sketch could provide a lot of traffic so it might be best to use the
//native port
#define Serial SerialUSB

unsigned long previousSend;

void setup()
{

  Serial.begin(115200);
  while(!Serial){;}// wait for serial port to connect before continuing
  Serial.print("Starting M2\r\n");
  
  // Initialize CAN0 and CAN1, Set the proper baud rates here
  Can0.begin(CAN_BPS_500K);
  Can1.begin(CAN_BPS_250K);
  
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

  pinMode(DS2,OUTPUT);
  digitalWrite(DS2,LOW);
  
  Serial.print("Setting RX filter\n");
  int filterStatus;
  filterStatus = Can0.setRXFilter(0,0x7E8,0xffffff,false);
  if (filterStatus >= 0){
    Serial.print("Set RX filter on mailbox ");
    Serial.print(filterStatus);
  } else{
    Serial.print("Failed to set RX filter on mailbox");
    Serial.print(filterStatus);
  }
  Serial.print("\n");
}

void printFrame(CAN_FRAME &frame) {
   Serial.print(millis());
   Serial.print(" ID: 0x");
   Serial.print(frame.id, HEX);
   Serial.print(" Len: ");
   Serial.print(frame.length);
   Serial.print(" Data: 0x");
   for (int count = 0; count < frame.length; count++) {
       Serial.print(frame.data.bytes[count], HEX);
       Serial.print(" ");
   }
   Serial.print("\r\n");
}

void sendFrame(){
  CAN_FRAME myFrame;
  myFrame.id = 0x730;
  myFrame.extended = false;
  
  myFrame.length = 8;
  myFrame.data.bytes[0] = 0x03;
  myFrame.data.bytes[1] = 0x22;
  myFrame.data.bytes[2] = 0x33;
  myFrame.data.bytes[3] = 0x02;
}

void loop(){
  CAN_FRAME incoming;

  delay(1000);
  digitalWrite(DS2,!digitalRead(DS2));// invert status of red led
  
  Serial.print(millis());
  Serial.print("\r\n");

  if (Can0.available() > 0) {
  Can0.read(incoming); 
  printFrame(incoming);
  }
  if (Can1.available() > 0) {
  Can1.read(incoming); 
  printFrame(incoming);
  }
}


