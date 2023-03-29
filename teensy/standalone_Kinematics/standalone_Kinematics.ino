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





// ODrive offsets from power up
// ratio is 10:1 so 1 'turn' is 36'.


float offSet20 = -0.3;      //ODrive 2, axis 0     // knee - right front
float offSet30 = 0.6;      //ODrive 3, axis 0     // knee - right rear
float offSet50 = 0.15;      //ODrive 5, axis 0     // knee - left front
float offSet60 = 0.05;      //ODrive 6, axis 0     // knee - left rear

float offSet21 = 0;      //ODrive 2, axis 1     // shoulder - right front
float offSet31 = 0.35;      //ODrive 3, axis 1     // shoulder - right rear
float offSet51 = 0.55;      //ODrive 5, axis 0     // shoulder - left front
float offSet61 =  0.05;      //ODrive 6, axis 1     // shoulder - left rear

float offSet10 = 0.27;      //ODrive 1, axis 0     // hips - right front
float offSet11 = 0.1;      //ODrive 1, axis 1     // hips - right back
float offSet40 = 0.07;      //ODrive 4, axis 0     // hips - left front
float offSet41 = 0.35;      //ODrive 4, axis 1     // hips - left back

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

void testMovement(){
  float pos0 = odrive1.GetPosition(0);
  float pos1 = odrive1.GetPosition(1);
  float pos2 = odrive2.GetPosition(0);
  float pos3 = odrive2.GetPosition(1);

  kinematics(1,0,0,350,0,0,0,0,0);
  delay(1000);
  kinematics(1,0,0,240,0,0,0,0,0);
}

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
  Serial.println("\nHello! Please enter height (-1 for gains, -2 for range, -3 leg 1 triangle walk,\n -4 xy triangle walk, -5 leg 1 and 4 triangle walk, -6 leg 1 range, -7 pre-programed motion)");
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
      kinematics(1,0,0,i,0,0,0,0,0);
    }
    delay(500);
    for (int i = 400; i>=100; i--){
      //delay(10);
      kinematics(1,0,0,i,0,0,0,0,0);
    }
    Serial.println("Range done");
  }
  else if(input== -3){
    for(int i = 0; i<3; i++){
      triangleWalk(1, -200,0, 350, 240, 100);
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
  else if(input== -5){ //leg 1 and 4 triangle walk
    for(int i = 0; i<3; i++){
      triangleWalk(1, -200,0, 350, 240, 100);
      triangleWalk(4, -200,0, 350, 240, 100);
    }
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
    transitionKinematics(1, -50, 50, 0, 0, 240, 350);
    transitionKinematics(1, 50, 50, 0, -75, 350, 350);
    transitionKinematics(1, 50, -50, -75, -75, 350, 350);
    transitionKinematics(1, -50, 50, -75, -75, 350, 240);
    transitionKinematics(1, 50, -550, -75, -75, 240, 350);
    transitionKinematics(1, -550, 0, -75, 0, 350, 240);
  }
  else if(input != 0){
    Serial.print("Running Kinematics with x: ");
    Serial.println(input);
    //kinematics(1,0,0,input,0,0,0,0,0);
    height_Test(input);
  }
  else{
    Serial.println("Skipping");
  }
}
