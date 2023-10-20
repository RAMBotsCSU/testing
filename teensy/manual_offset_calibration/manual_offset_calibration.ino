#include <Ramp.h>
#include <ODriveArduino.h>
#include <HardwareSerial.h>
#include "config.h"


int interpFlag = 0;
long previousInterpMillis = 0;    // set up timers

unsigned long currentMillis;
long previousMillis = 0;    // set up timers
long interval = 10;        // time constant for timer
unsigned long count;
int toggleTopOld;
int remoteState;
int remoteStateOld;  

int requested_state;
int mode;
int modeOld;
int modeFlag;
int menuFlag;
int modeConfirm;
int modeConfirmFlag = 0;
int runMode = 0;

// Printing with stream operator
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }




HardwareSerial& odrive1Serial = Serial1;
HardwareSerial& odrive2Serial = Serial2;
HardwareSerial& odrive3Serial = Serial3;
HardwareSerial& odrive4Serial = Serial4;
HardwareSerial& odrive5Serial = Serial5;
HardwareSerial& odrive6Serial = Serial6;

//ODrive Objects
ODriveArduino odrive1(odrive1Serial);
ODriveArduino odrive2(odrive2Serial);
ODriveArduino odrive3(odrive3Serial);
ODriveArduino odrive4(odrive4Serial);
ODriveArduino odrive5(odrive5Serial);
ODriveArduino odrive6(odrive6Serial);

class Interpolation {
  public:
    rampInt myRamp;
    int interpolationFlag = 0;
    int savedValue;

    int go(int input, int duration) {

      if (input != savedValue) {   // check for new data
        interpolationFlag = 0;
      }
      savedValue = input;          // bookmark the old value

      if (interpolationFlag == 0) {                                        // only do it once until the flag is reset
        myRamp.go(input, duration, LINEAR, ONCEFORWARD);              // start interpolation (value to go to, duration)
        interpolationFlag = 1;
      }

      int output = myRamp.update();
      return output;
    }
};    // end of class

Interpolation interpFRX;        // interpolation objects
Interpolation interpFRY;
Interpolation interpFRZ;
Interpolation interpFRT;

Interpolation interpFLX;        // interpolation objects
Interpolation interpFLY;
Interpolation interpFLZ;
Interpolation interpFLT;

Interpolation interpBRX;        // interpolation objects
Interpolation interpBRY;
Interpolation interpBRZ;
Interpolation interpBRT;

Interpolation interpBLX;        // interpolation objects
Interpolation interpBLY;
Interpolation interpBLZ;
Interpolation interpBLT;

void printVals(ODriveArduino odrive, int x, int y, int z){
//  Serial2 << "w axis" << 0 << ".encoder.shadow_count " << '\n';
//  Serial2 << "w axis" << 1 << ".encoder.shadow_count " << '\n';
  String shadowCountE, shadowCountS;
  Serial.print(x);
  Serial.print(" ");
  Serial.print(y);
  Serial.print(" ");
  Serial.print(z);
  Serial.print(" ");
  Serial2 <<"r axis1.encoder.shadow_count\n";
  while (Serial2.available() == 0) {}
  Serial << odrive.readFloat();
  Serial.print(" ");
  Serial2 <<"r axis0.encoder.shadow_count\n";
  while (Serial2.available() == 0) {}
  Serial << odrive.readFloat();
  Serial.println();
}

String getInput (String msg) {
  Serial.print(msg);

  while (Serial.available() == 0) {
    // Wait for user input
  }

  String inputVal = Serial.readString(); // Read the user input as a string

  return inputVal;
}

// String getInput(String msg) {
//   Serial.print(msg);
//   String inputVal = "";

//   while (true) {
//     if (Serial.available() > 0) {
//       char c = Serial.read();
//       if (c == '\n' || c == '\r') {
//         break; // Exit the loop when a newline character is received
//       } else {
//         inputVal += c; // Add the character to the input string
//       }
//     }
//   }

//   return inputVal;
// }

float getFloatInput(String msg) {
  Serial.print(msg);

  while (Serial.available() == 0) {
    // Wait for user input
  }

  String inputVal = Serial.readString(); // Read the user input as a string

  return inputVal.toFloat(); // Convert the string to a float and return it
}


void setup() {
  Serial.begin(9600);
  odrive1Serial.begin(115200);
  odrive2Serial.begin(115200);
  odrive3Serial.begin(115200);
  odrive4Serial.begin(115200);
  odrive5Serial.begin(115200);
  odrive6Serial.begin(115200);
}

int input = -1;
int lastVal = 0;
int tempVal = -1;

int stage = 0;

void loop() {
  Serial.println("\nHello! Please enter height (-1 , -2 all leg triangle walk, -3 single leg triangle walk,\n -4 xy triangle walk, -5 all leg triangle walk, -6 leg 1 range, -7 pre-programed motion)");
  while (Serial.available() == 0) {}
  input = Serial.parseInt();


  if(input == -1){
    Serial2 << "w axis" << 0 << ".motor.config.direction " << 1 << '\n';
    modifyGains();
    //applyOffsets2();
    Serial.println("Gains Modified");
  }
  else if(input == -2){ // All legs triangle walk
    triangleWalk(1, -200,0, 350, 240, 100); //fr
    triangleWalk(4, -200,0, 350, 240, 100); //fl?
    triangleWalk(2, -200,0, 350, 240, 100); //bl?
    triangleWalk(3, -200,0, 350, 240, 100); //br
  }
  else if(input== -3){

    Serial.println("Single Leg triangle walk.");
    String receivedString = getInput("Select a leg (LF, LB, RF, RB): ");
    
    int legToRun = 0;
    // If a newline character is received, it indicates the end of the string
    Serial.println(receivedString);

    if (receivedString == "LF") {
      Serial.println("Left Front leg selected.");
      legToRun = 2;
    }
    else if (receivedString == "LB") {
      Serial.print("Left Back leg selected.");
      legToRun = 3;
    }
    else if (receivedString == "RF") {
      Serial.print("Right Front leg selected.");
      legToRun = 1;
    }
    else if (receivedString == "RB") {
      Serial.print("Right Back leg selected.");
      legToRun = 4;
    }
    else {
      Serial.println("Invalid leg identifier. Use (LF, LB, RF, RB). Process cancelled.");
    }

    String directionInput = getInput("Direction to walk (F - forward or R - reverse): ");

    if (directionInput == "R") {
      triangleWalkReverse(legToRun, -200,0, 350, 240, 100);
    } else if (directionInput == "F") {
      triangleWalk(legToRun, -200,0, 350, 240, 100);
    }

  }
  else if(input== -4){
    Serial.println("Modify Offsets.");
    String legInput = getInput("Select a leg (LF, LB, RF, RB): ");
    String jointInput = getInput("Select a joint (hip, shoulder, knee): ");
    float newOffset = getFloatInput("Enter a new offset: ");
    int legToRun = 0;
    if (legInput == "LF") {
      Serial.println("Left Front leg selected.");
      legToRun = 2;
    }
    else if (legInput == "LB") {
      Serial.print("Left Back leg selected.");
      legToRun = 3;
    }
    else if (legInput == "RF") {
      Serial.print("Right Front leg selected.");
      legToRun = 1;
    }
    else if (legInput == "RB") {
      Serial.print("Right Back leg selected.");
      legToRun = 4;
    }
    else {
      Serial.println("Invalid leg identifier. Use (LF, LB, RF, RB). Process cancelled.");
    }
    editOffset(legInput, jointInput, newOffset);
    triangleWalk(legToRun, -200,0, 350, 240, 100);
  }
  else if(input != 0){
    Serial.print("Running Kinematics with x: ");
    Serial.println(input);
    //kinematics(1,0,0,input,0,0,0,0,0);
    height_Test(input);
  }
  else{
    Serial.print("Skipping");
  }

}

