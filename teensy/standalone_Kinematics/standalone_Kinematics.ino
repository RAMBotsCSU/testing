#include <Ramp.h>
#include <ODriveArduino.h>
#include <HardwareSerial.h>

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

void loop() {
  Serial.println("\nHello! Please enter height (-1 for gains, -2 for range, -3 leg 1 triangle walk,\n -4 xy triangle walk, -5 all leg triangle walk, -6 leg 1 range, -7 pre-programed motion)");
  while (Serial.available() == 0) {}
  input = Serial.parseInt();
  if(input == -1){
    Serial2 << "w axis" << 0 << ".motor.config.direction " << 1 << '\n';
    modifyGains();
    //applyOffsets2();
    Serial.println("Gains Modified");
  }
  else if(input == -2){
    Serial.println("Testing Range");
    for (int i = 100; i<=400; i++){
      //delay(10);
      kinematics(3,0,0,i,0,0,0,0,0);
    }
    delay(500);
    for (int i = 400; i>=100; i--){
      //delay(10);
      kinematics(3,0,0,i,0,0,0,0,0);
    }
    Serial.println("Range done");
  }
  else if(input== -3){
    for(int i = 0; i<3; i++){
      triangleWalk(3, -200,0, 350, 240, 100);
    }
  }
  else if(input== -4){
    tempVal = 0;
    for(int i = -100; i < 0; i = i+25){               //x -> -100 to 100
      triangleWalk(1, i, tempVal, 350, 240, 100);     //y -> -25 to 25
      tempVal = tempVal - 25;                         //z -> 240 to 350
    }
    for(int i = 0; i < 100; i = i+25){
      triangleWalk(1, i, tempVal, 350, 240, 100);
      tempVal = tempVal + 25;
    }
  }
  else if(input== -5){ //all leg 1 and 4 triangle walk
    //for(int i = 0; i<3; i++){
      triangleWalk(1, -200,0, 350, 240, 100); //fr
      triangleWalk(4, -200,0, 350, 240, 100); //fl?
      triangleWalk(2, -200,0, 350, 240, 100); //bl?
      triangleWalk(3, -200,0, 350, 240, 100); //br
    //}
  }
  else if (input == -6){
    float lastX = 0;
    for (int x = -250; x <= 400; x = x+10){
      Serial.print("X: ");
      Serial.println(x);
      transitionKinematics(1, lastX, x, 0, 0, 240, 390);
      lastX = x;
      transitionKinematics(1, x, lastX, 0, 0, 390, 240);
    }
    transitionKinematics(1,lastX,0,0,0,390,250);
  }
  else if(input== -7){
    kinematics(1,-50,0,240,0,0,0,0,0);
    //from to
    transitionKinematics(3, 0, 100, 0, 0, 350, 350);
    transitionKinematics(3, 100, -100, 0, 0, 350, 350);
    transitionKinematics(3, -100, 100, 0, 0, 350, 350);
    transitionKinematics(3, 100, -100, 0, 0, 350, 350);
    transitionKinematics(3, -100, 100, 0, 0, 350, 350);
    transitionKinematics(3, 100, -0, 0, 0, 350, 350);
  }
  else if(input== -8){
    for (int heightLeg = 380; heightLeg >= 280; heightLeg--){
      kinematics (1, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // front right
      kinematics (2, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // front left
      kinematics (3, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // back left
      kinematics (4, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // back right 
    }
    for (int heightLeg = 280; heightLeg <= 380; heightLeg++){
      kinematics (1, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // front right
      kinematics (2, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // front left
      kinematics (3, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // back left
      kinematics (4, 0, 0, heightLeg, 0, 0, 0, 0, 0);   // back right 
    } 
  }  
  else if(input== -9){
    for (float roll = 0; roll <= 20; roll = roll+0.5){
      kinematics (1, 0, 0, 380, roll, 0, 0, 0, 0);   // front right
      kinematics (2, 0, 0, 380, roll, 0, 0, 0, 0);   // front left
      kinematics (3, 0, 0, 380, roll, 0, 0, 0, 0);   // back left
      kinematics (4, 0, 0, 380, roll, 0, 0, 0, 0);   // back right 
      //delay(500);
    }
    for (float roll = 20; roll >= -20; roll=roll-0.5){
      kinematics (1, 0, 0, 380, roll, 0, 0, 0, 0);   // front right
      kinematics (2, 0, 0, 380, roll, 0, 0, 0, 0);   // front left
      kinematics (3, 0, 0, 380, roll, 0, 0, 0, 0);   // back left
      kinematics (4, 0, 0, 380, roll, 0, 0, 0, 0);   // back right 
      //delay(500);
    }
    for (float roll = -20; roll <= 0; roll=roll+0.5){
      kinematics (1, 0, 0, 380, roll, 0, 0, 0, 0);   // front right
      kinematics (2, 0, 0, 380, roll, 0, 0, 0, 0);   // front left
      kinematics (3, 0, 0, 380, roll, 0, 0, 0, 0);   // back left
      kinematics (4, 0, 0, 380, roll, 0, 0, 0, 0);   // back right 
      //delay(500);
    }/*
    kinematics (1, 0, 0, 380, -10, 0, 0, 1, 0000000000000.1);   // front right
    kinematics (2, 0, 0, 380, -10, 0, 0, 1, 0000000000000.1);   // front left
    kinematics (3, 0, 0, 380, -10, 0, 0, 1, 0000000000000.1);   // back left
    kinematics (4, 0, 0, 380, -10, 0, 0, 1, 0000000000000.1);   // back right 
    delay(5000);

    kinematics (1, 0, 0, 380, 10, 0, 0, 1, 1);   // front right
    kinematics (2, 0, 0, 380, 10, 0, 0, 1, 1);   // front left
    kinematics (3, 0, 0, 380, 10, 0, 0, 1, 1);   // back left
    kinematics (4, 0, 0, 380, 10, 0, 0, 1, 1);   // back right 
    delay(5000);

    kinematics (1, 0, 0, 380, 0, 0, 0, 1, 10000000000000);   // front right
    kinematics (2, 0, 0, 380, 0, 0, 0, 1, 10000000000000);   // front left
    kinematics (3, 0, 0, 380, 0, 0, 0, 1, 10000000000000);   // back left
    kinematics (4, 0, 0, 380, 0, 0, 0, 1, 10000000000000);   // back right */
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
