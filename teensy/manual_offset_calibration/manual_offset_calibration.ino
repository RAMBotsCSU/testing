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

  Serial.println(inputVal);

  return inputVal;
}


float getFloatInput(String msg) {
  Serial.print(msg);

  while (Serial.available() == 0) {
    // Wait for user input
  }

  String inputVal = Serial.readString(); // Read the user input as a string

  Serial.println(inputVal);

  return inputVal.toFloat(); // Convert the string to a float and return it
}

int selectLeg(String legCode) {
  int legToRun = 0;
  if (legCode == "LF") {
      Serial.println("Left Front leg selected.");
      legToRun = 2;
  }
  else if (legCode == "LB") {
    Serial.print("Left Back leg selected.");
    legToRun = 3;
  }
  else if (legCode == "RF") {
    Serial.print("Right Front leg selected.");
    legToRun = 1;
  }
  else if (legCode == "RB") {
    Serial.print("Right Back leg selected.");
    legToRun = 4;
  }
  else {
    Serial.println("Invalid leg identifier. Use (LF, LB, RF, RB). Process cancelled.");
  }
  return legToRun;
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
int gainFlag = 0;

void loop() {
  Serial.println("\nManual Configuration Started. (-1 all legs walk, -2 single leg walk, -3 Modify Offset, -4 Print Offsets)\n");
  if(gainFlag == 0){
    Serial2 << "w axis" << 0 << ".motor.config.direction " << 1 << '\n';
    modifyGains();
    //applyOffsets2();
    Serial.println("Gains Modified");
    gainFlag = 1;
  }
  while (Serial.available() == 0) {}
  input = Serial.parseInt();


  if(input == -1){ // All legs triangle walk
    Serial.println("All legs triangle walk.");
    triangleWalk(1, -200,0, 350, 240, 100); //fr
    triangleWalk(4, -200,0, 350, 240, 100); //fl?
    triangleWalk(2, -200,0, 350, 240, 100); //bl?
    triangleWalk(3, -200,0, 350, 240, 100); //br
  }
  else if(input== -2){

    Serial.println("Single leg triangle walk.");
    String receivedString = getInput("Select a leg (LF, LB, RF, RB): ");
    
    int legToRun = selectLeg(receivedString);

    triangleWalk(legToRun, -200,0, 350, 240, 100);
  }
  else if(input== -3){
    Serial.println("Modify Offsets.");
    String legInput = getInput("Select a leg (LF, LB, RF, RB): ");
    String jointInput  = "";
    while (jointInput != "exit") {
      Serial.print("Modifyig ");
      Serial.print(legInput);
      Serial.println(" leg, enter exit to leave.");

      jointInput = getInput("Select a joint (hip, shoulder, knee): ");
      String directionInput = getInput("Direction to offset (F - forward or B - backward): ");
      float offsetDelta = getFloatInput("Enter offset delta: ");
      
      editOffset(legInput, jointInput, directionInput, offsetDelta);

      int legToRun = selectLeg(legInput);
      Serial.println("Applying Offset");
      triangleWalk(legToRun, -200,0, 350, 240, 100);
    }
    
    
  }
  else if(input== -4){
    String hip_end = ";  // HIP";
    String shoulder_end = ";  // SHOULDER";
    String knee_end = ";  // KNEE";

    Serial.println("Printing Offsets:");
    Serial.println("");

    Serial.println("// LEFT FRONT LEG");
    Serial.print("float offSet40 = ");
    Serial.print(offSet40);
    Serial.println(hip_end);

    Serial.print("float offSet51 = ");
    Serial.print(offSet51);
    Serial.println(shoulder_end);

    Serial.print("float offSet50 = ");
    Serial.print(offSet50);
    Serial.println(knee_end);


    Serial.println("");

    Serial.println("// LEFT BACK LEG");
    Serial.print("float offSet41 = ");
    Serial.print(offSet41);
    Serial.println(hip_end);

    Serial.print("float offSet61 = ");
    Serial.print(offSet61);
    Serial.println(shoulder_end);

    Serial.print("float offSet60 = ");
    Serial.print(offSet60);
    Serial.println(knee_end);


    Serial.println("");

    Serial.println("// RIGHT FRONT LEG");
    Serial.print("float offSet10 = ");
    Serial.print(offSet10);
    Serial.println(hip_end);

    Serial.print("float offSet21 = ");
    Serial.print(offSet21);
    Serial.println(shoulder_end);

    Serial.print("float offSet20 = ");
    Serial.print(offSet20);
    Serial.println(knee_end);

    Serial.println("");

    Serial.println("// RIGHT BACK LEG");
    Serial.print("float offSet11 = ");
    Serial.print(offSet11);
    Serial.println(hip_end);

    Serial.print("float offSet31 = ");
    Serial.print(offSet31);
    Serial.println(shoulder_end);

    Serial.print("float offSet30 = ");
    Serial.print(offSet30);
    Serial.println(knee_end);

  }
  else if (input== -5) {
    float tick = getFloatInput("Select encoder tick:");
    driveJoints (60, tick);
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

