#include <Ramp.h>
#include <ODriveArduino.h>
#include <HardwareSerial.h>
#include "config.h"
#include <Wire.h>

int maxLegHeight = 380;
int minLegHeight = 320;


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

//gyro variables
float LegRollFiltered = 0;
float LegPitchFiltered = 0;
float RateRoll, RatePitch, RateYaw;
float RateCalibrationRoll, RateCalibrationPitch, RateCalibrationYaw;
int RateCalibrationNumber;
float AccX, AccY, AccZ;
float AngleRoll, AnglePitch;

float KalmanAngleRoll=0, KalmanUncertaintyAngleRoll=2*2;
float KalmanAnglePitch=0, KalmanUncertaintyAnglePitch=2*2;
float Kalman1DOutput[]={0,0};

// Printing with stream operator
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }




HardwareSerial& odrive1Serial = Serial1;

//ODrive Objects
ODriveArduino odrive1(odrive1Serial);

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

Interpolation interpX;        // interpolation objects
Interpolation interpY;
Interpolation interpZ;
Interpolation interpT;


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
}

int input = -1;
int lastVal = 0;
int tempVal = -1;

int stage = 0;
int gainFlag = 0;

void loop() {
  currentMillis = millis();
  Serial.println("\nManual Configuration Started. (-1 all legs walk, -2 single leg walk, -3 Modify Offset, -4 Print Offsets)\n");
  if(gainFlag == 0){
    // Serial2 << "w axis" << 0 << ".motor.config.direction " << 1 << '\n';
    modifyGains();
    //applyOffsets2();
    Serial.println("Gains Modified");
    gainFlag = 1;
  }
  while (Serial.available() == 0) {}
  input = Serial.parseInt();


  if(input== -1){

    Serial.println("Single leg triangle walk. Enter 9 to exit loop.");
    
    while(Serial.parseInt() != 9) {
      triangleWalk(1, -200,0, 350, 240, 100);
    }
    
  }
  else if (input== -2) {
    float tick = getFloatInput("Select encoder tick:");
    driveJoints (10, tick);
  }
  else if (input == -3) {
    float tick = getFloatInput("Select encoder tick:");
    driveJoints (11, tick);
    
  }
  else if (input == -4) {
    Serial.println("Open dog walk. Enter 9 to exit loop.");
    while(Serial.parseInt() != 9) {
      currentMillis = millis();
      if (currentMillis - previousMillis >= 1000) {
        previousMillis = currentMillis;
        openDogWalkCycle(1, 0, 0, 0, 0, false);
      }
      
    }
    
  }
  else if (input == -5) {
    // kinematics (1, 0, 0, maxLegHeight, 0, 0, 0, 1, (1000*0.8));
    // height_Test(12);
    // currentMillis = millis();
    // previousMillis = currentMillis;
    Serial.println("kinematics test");
    // Serial.println(currentMillis - previousMillis);
    // while (currentMillis - previousMillis < 100) {
    //   Serial.println("Pushups Loop");
    //   currentMillis = millis();
    //   kinematics (1, 0, 0, 0, 0, 0, 0, 0, 0);
    // }
    kinematics (1, 0, 0, 100, 0, 0, 0, 1, 100);
  }
  else if (input == -6) {
    // kinematics (1, 10, 0, maxLegHeight, 0, 0, 0, 1, (1000*0.8));
    currentMillis = millis();
    previousMillis = currentMillis;
    Serial.println("Pushups");
    Serial.println(currentMillis - previousMillis);
    while (currentMillis - previousMillis < 100) {
      Serial.println("Pushups Loop");
      currentMillis = millis();
      pushUps(0);
    }
    // height_Test(12);
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

