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
int timeBetweenRequests = 250;

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
  idx +=1;
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
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0xF4;
  framesToSend[idx].data.bytes[3] = 0x0D;
    
  // leftFronWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x06;
      
  // rightFronWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x07;
      
  // leftRearWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x08;
      
  // rightRearWheelSpeed
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x09;
      
  // longitudinalAcceleration
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x11;
      
  // lateralAcceleration
  idx +=1; 
  framesToSend[idx].id = 0x760;
  framesToSend[idx].extended = false;
  framesToSend[idx].length = 8;
  framesToSend[idx].data.bytes[0] = 0x03;
  framesToSend[idx].data.bytes[1] = 0x22;
  framesToSend[idx].data.bytes[2] = 0x2B;
  framesToSend[idx].data.bytes[3] = 0x0C;
  
  Can0.begin(CAN_BPS_500K);
  //By default there are 7 mailboxes for each device that are RX boxes
  //This sets each mailbox to have an open filter that will accept extended
  //or standard frames

  //deny all CAN packets by default
  int filter;
  //extendeds
  for (filter = 0; filter < 3; filter++) {
    Can0.setRXFilter(filter, 0, 0xffffff, true);
    Can1.setRXFilter(filter, 0, 0xffffff, true);
  }
  //standard
  for (int filter = 3; filter < 7; filter++) {
    Can0.setRXFilter(filter, 0, 0xffffff, false);
    Can1.setRXFilter(filter, 0, 0xffffff, false);
  }

  Serial.print("Setting RX filter\n");
  int filterStatus;
  filterStatus = Can0.setRXFilter(0, 0x738, 0xffffff, false);
  filterStatus = Can0.setRXFilter(1, 0x739, 0xffffff, false);
  filterStatus = Can0.setRXFilter(2, 0x7E8, 0xffffff, false);
  filterStatus = Can0.setRXFilter(3, 0x768, 0xffffff, false);
  
  if (filterStatus >= 0) {
    Serial.print("Set RX filter on mailbox ");
    Serial.print(filterStatus);
  } else {
    Serial.print("Failed to set RX filter on mailbox");
    Serial.print(filterStatus);
  }
  
  Serial.print("\n");

  Serial.print("Waiting for computer to request time in a very hacky way...\n");
  while(!Serial.available()){}
  Serial.print(millis());
  delay(1000);
}

void writeFrameToSerial(CAN_FRAME *frame) {
  digitalWrite(DS6, !digitalRead(DS6)); // invert status of green led
  Serial.print(millis());
  Serial.print(",");
  //Serial.print(" ID: 0x");
  Serial.print(frame->id, HEX);
  Serial.print(",");
  //Serial.print(" Len: ");
  Serial.print(frame->length);
  //Serial.print(" Data: 0x");
  for (int count = 0; count < frame->length; count++) {
    Serial.print(",");
    Serial.print(frame->data.bytes[count], HEX);
  }
  Serial.print("\n");
}

void loop() {
  /*
  CAN_FRAME fakeFrame;
  fakeFrame.id = 0x731;
  fakeFrame.length = 8;
  fakeFrame.data.bytes[0] = 0x01;
  fakeFrame.data.bytes[1] = 0x02;
  fakeFrame.data.bytes[2] = 0x03;
  fakeFrame.data.bytes[3] = 0x04;
  fakeFrame.data.bytes[4] = 0x05;
  fakeFrame.data.bytes[5] = 0x06;
  fakeFrame.data.bytes[6] = 0x07;
  fakeFrame.data.bytes[7] = 0x08;
  writeFrameToSerial(&fakeFrame);
  delay(100);
*/
  
  CAN_FRAME frame;
  if (lastSend+timeBetweenRequests <= millis()){
    digitalWrite(DS5, !digitalRead(DS5)); // invert status of first yellow LED
    lastSend = millis();
    for (int ii=0;ii<numFrames;ii++){ // want to clear the buffers as they come in
      Can0.sendFrame(framesToSend[ii]);
      delay(20);// need to wait so Tx buffer does not get overwritten, also helps in Rx
      while (Can0.available()>0){
        Can0.read(frame);
        writeFrameToSerial(&frame);
      }
    }
  }
}


