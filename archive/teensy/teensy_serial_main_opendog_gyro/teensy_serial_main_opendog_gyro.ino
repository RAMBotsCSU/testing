//********************************************************
//* This is a simple test for the teensy that recieves   *
//* a string over the serial line, appends some values   *
//* then sends it back over serial. This method includes *
//* padding functions for the serial communication to    *
//* speed up the communication.                          *
//********************************************************

// ramp lib
#include <Ramp.h>
#include <ODriveArduino.h>
#include <HardwareSerial.h>

//Setup and set the pin for the LED
int led = 13;
int setInd = -1;
int currentMode = -1;
String currentModeString = "-1";
float setVal = -1.1;
float movementArr[7]; //0 = strafe, 1 = forback, 2 = roll, 3 = turn, 4 = pitch, 5 = height, 6 = yaw
String keyWord = "00";
int keyWord_int = 00;

float bounded_x_test_leg = 0;
float bounded_y_test_leg = 0;
float bounded_z_test_leg = 295;
String bounded_x_test_leg_string = "";
String bounded_y_test_leg_string = "";
String bounded_z_test_leg_string = "";

float RLR = 0;
float RFB = 0;
float LT = 0;

float longLeg1;
float shortLeg1;
float legLength1;
float longLeg2;
float shortLeg2;
float legLength2;
float footOffset;

int timer1;   // FB gait timer
int timer2;   // LR gait timer
int timer3;   // Yaw gait timer
float timerScale;   // resulting timer after calcs
float timerScale2;   // multiplier

float RLRFiltered = 0;
float RFBFiltered = 0;
float RTFiltered = 340;
float LLRFiltered = 0;
float LFBFiltered = 0;
float LTFiltered = 0;
float LegRollFiltered = 0;
float LegPitchFiltered = 0;
int filterFlag1 = 0;


int stepFlag = 0;
long previousStepMillis = 0;
int stepStartFlag = 0;

float fr_RFB;
float fl_RFB;
float bl_RFB;
float br_RFB;
float fr_RLR;
float fl_RLR;
float bl_RLR;
float br_RLR;
float fr_LT;
float fl_LT;
float bl_LT;
float br_LT;

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

String fr_RFB_string, fr_RLR_string, legLength1_string, legLength2_string,timerScale_string = "";
String RFBFiltered_string, RLRFiltered_string, LTFiltered_string = "";


// Printing with stream operator
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }





// ODrive offsets from power up
// ratio is 10:1 so 1 'turn' is 36'.


float offSet20 = 0.3;      //ODrive 2, axis 0     // knee - right front
float offSet30 = -0.2;      //ODrive 3, axis 0     // knee - right rear
float offSet50 = -0.7;      //ODrive 5, axis 0     // knee - left front
float offSet60 = 0.2;      //ODrive 6, axis 0     // knee - left rear

float offSet21 = 0.1;      //ODrive 2, axis 1     // shoulder - right front
float offSet31 = 0.0;      //ODrive 3, axis 1     // shoulder - right rear
float offSet51 = -0.6;      //ODrive 5, axis 1     // shoulder - left front
float offSet61 =  -0.1;      //ODrive 6, axis 1     // shoulder - left rear

float offSet10 = -0.4;      //ODrive 1, axis 0     // hips - right front
float offSet11 = 0.3;      //ODrive 1, axis 1     // hips - right back
float offSet40 = 0.25;      //ODrive 4, axis 0     // hips - left front
float offSet41 = 0.2;      //ODrive 4, axis 1     // hips - left back



/*
The contents of this code and instructions are the intellectual property of Carbon Aeronautics. 
The text and figures in this code and instructions are licensed under a Creative Commons Attribution - Noncommercial - ShareAlike 4.0 International Public Licence. 
This license lets you remix, adapt, and build upon your work non-commercially, as long as you credit Carbon Aeronautics 
(but not in any way that suggests that we endorse you or your use of the work) and license your new creations under the identical terms.
This code and instruction is provided "As Is” without any further warranty. Neither Carbon Aeronautics or the author has any liability to any person or entity 
with respect to any loss or damage caused or declared to be caused directly or indirectly by the instructions contained in this code or by 
the software and hardware described in it. As Carbon Aeronautics has no control over the use, setup, assembly, modification or misuse of the hardware, 
software and information described in this manual, no liability shall be assumed nor accepted for any resulting damage or injury. 
By the act of copying, use, setup or assembly, the user accepts all resulting liability.
1.0  29 December 2022 -  initial release
*/

#include <Wire.h>
float RateRoll, RatePitch, RateYaw;
float RateCalibrationRoll, RateCalibrationPitch, RateCalibrationYaw;
int RateCalibrationNumber;
float AccX, AccY, AccZ;
float AngleRoll, AnglePitch;

float KalmanAngleRoll=0, KalmanUncertaintyAngleRoll=2*2;
float KalmanAnglePitch=0, KalmanUncertaintyAnglePitch=2*2;
float Kalman1DOutput[]={0,0};

void kalman_1d(float KalmanState, float KalmanUncertainty, float KalmanInput, float KalmanMeasurement) {
  KalmanState=KalmanState+0.004*KalmanInput;
  KalmanUncertainty=KalmanUncertainty + 0.004 * 0.004 * 4 * 4;
  float KalmanGain=KalmanUncertainty * 1/(1*KalmanUncertainty + 3 * 3);
  KalmanState=KalmanState+KalmanGain * (KalmanMeasurement-KalmanState);
  KalmanUncertainty=(1-KalmanGain) * KalmanUncertainty;
  Kalman1DOutput[0]=KalmanState; 
  Kalman1DOutput[1]=KalmanUncertainty;
}
void gyro_signals(void) {
  Wire.beginTransmission(0x68);
  Wire.write(0x1A);
  Wire.write(0x05);
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x10);
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission(); 
  Wire.requestFrom(0x68,6);
  int16_t AccXLSB = Wire.read() << 8 | Wire.read();
  int16_t AccYLSB = Wire.read() << 8 | Wire.read();
  int16_t AccZLSB = Wire.read() << 8 | Wire.read();
  Wire.beginTransmission(0x68);
  Wire.write(0x1B); 
  Wire.write(0x8);
  Wire.endTransmission();     
  Wire.beginTransmission(0x68);
  Wire.write(0x43);
  Wire.endTransmission();
  Wire.requestFrom(0x68,6);
  int16_t GyroX=Wire.read()<<8 | Wire.read();
  int16_t GyroY=Wire.read()<<8 | Wire.read();
  int16_t GyroZ=Wire.read()<<8 | Wire.read();
  RateRoll=(float)GyroX/65.5;
  RatePitch=(float)GyroY/65.5;
  RateYaw=(float)GyroZ/65.5;
  AccX=(float)AccXLSB/4096;
  AccY=(float)AccYLSB/4096;
  AccZ=(float)AccZLSB/4096;
  AngleRoll=atan(AccY/sqrt(AccX*AccX+AccZ*AccZ))*1/(3.142/180);
  AnglePitch=-atan(AccX/sqrt(AccY*AccY+AccZ*AccZ))*1/(3.142/180);
}

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

ODriveArduino odrArr[6] = {odrive1, odrive2, odrive3, odrive4, odrive5, odrive6};

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  odrive1Serial.begin(115200);
  odrive2Serial.begin(115200);
  odrive3Serial.begin(115200);
  odrive4Serial.begin(115200);
  odrive5Serial.begin(115200);
  odrive6Serial.begin(115200);
  Serial7.begin(19200);
  modifyGains();
  applyOffsets1();
  applyOffsets2();

  //odrive1Serial.print("sr\n");
  //odrive2Serial.print("sr\n");
  //odrive3Serial.print("sr\n");
  //odrive4Serial.print("sr\n");
  //odrive5Serial.print("sr\n");
  //odrive6Serial.print("sr\n");
/*
  int closedLoop = 8;
  for (int i = 0; i<2; i++){
    for (int axis = 0; axis<2; axis++){ //each axis in the odrive
      float indexFound = 0;
      float found = 0;
      while (found == 0){
        indexFound = odrArr[i].IndexFound(axis);
        if (indexFound > 0.){
          found = 1;
          delay(5);
          odrArr[i].run_state(axis,closedLoop, false);
          //Serial.print(i);
          //Serial.println(axis);
        }
      }
    } 
  }*/
  Wire.setClock(400000);
  Wire.begin();
  delay(250);
  Wire.beginTransmission(0x68); 
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();
  for (RateCalibrationNumber=0; RateCalibrationNumber<2000; RateCalibrationNumber ++) {
    gyro_signals();
    RateCalibrationRoll+=RateRoll;
    RateCalibrationPitch+=RatePitch;
    RateCalibrationYaw+=RateYaw;
    delay(1);
  }
  RateCalibrationRoll/=2000;
  RateCalibrationPitch/=2000;
  RateCalibrationYaw/=2000;
}

String getArrStr(){
  String stringFinal;
  String String1 = "Teensy: strafe:";
  String String2 = ", forback:";
  String String3 = ", roll:";
  String String4 = ", turn:";
  String String5 = ", pitch:";
  String String6 = ", height:";
  String String7 = ", yaw:";
  double Val1 = movementArr[0];
  double Val2 = movementArr[1];
  double Val3 = movementArr[2];
  double Val4 = movementArr[3];
  double Val5 = movementArr[4];
  double Val6 = movementArr[5];
  double Val7 = movementArr[6];

  stringFinal = String1 + Val1 + String2 + Val2 + String3 + Val3 + String4 + Val4 + String5 + Val5 + String6 + Val6 + String7 + Val7;
  return stringFinal;
  
}

//Function to pad the string to 120 chars (serial uses 127, but the write command adds 7 chars)
String padStr(String str){
  int target = 120-str.length();
  for (int i = 0; i < target; i++) {
    str += "~";
  }
  return str;
}

//Function to remove the padding of strings
String rmPadStr(String str){
  for (int i = 0; i < str.length(); i++){
    if (str[i] == '~'){
      str.remove(i);
      return str;
    }
  }
  return str;
}


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
}

// should probably be using constrain() instead....
float mapValue(float val, float lower_range, float upper_range){ // map joystick range [-1,1] to [lower,upper]
    float normalizedValue = (val + 1.00) / 2.00;
    return lower_range + (normalizedValue * (upper_range - lower_range));
}

int keyword_to_int(String keyWord){ // convert 2 character keyword to an int value to use switch statements
    return (keyWord[0] - '0') * 10 + (keyWord[1] - '0');
}

int L3_x = 0;
int L3_y = 0;
int R3_x = 0;
int R3_y = 0;


String serial_input = "";
String readStr = "";
String printString = "hampter";

//Main loop to be executed
void loop() {
    Serial7.println("hello world");
    serial_input = Serial.readString();  
    serial_input.trim();                                     //Remove any \r \n whitespace at the end of the String
    serial_input = rmPadStr(serial_input);                        //Remove any padding from readStr
    //Serial.println(serial_input);      //Print to the serial buffer 
    printString =  "fr_RFB: " + fr_RFB_string + ", fr_RLR: " + fr_RLR_string + ", legLength1: " + legLength1_string;
    Serial.println(printString);
    //Serial.println("L3_x: " + String(L3_x) + ", L3_y: " + String(L3_y) + ", R3_x: " + String(R3_x) + ", R3_y: " + String(R3_y));
    //Serial.println("fr_RFB: " + fr_RFB_string + ", fr_RLR: " + fr_RLR_string + ", legLength1: " + legLength1_string);
    //Serial.println("fr_RFB: " + fr_RFB_string);

    //3276
    
    currentMillis = millis();
    if (currentMillis - previousMillis >= 10) {  // start timed event

        previousMillis = currentMillis;
        
        //readStr = serial_input;
        
        // extract the four integers from the string
         L3_x = serial_input.substring(serial_input.indexOf("(")+1, serial_input.indexOf(",")).toInt();
         L3_y = serial_input.substring(serial_input.indexOf(",")+2, serial_input.indexOf(")")).toInt();
         R3_x = serial_input.substring(serial_input.lastIndexOf("(")+1, serial_input.lastIndexOf(",")).toInt();
         R3_y = serial_input.substring(serial_input.lastIndexOf(",")+2, serial_input.lastIndexOf(")")).toInt();

         RFB = map(L3_y, -32767, 32767, -50, 50);
         //mapValue(L3_y, -50,50);
         RLR = map(L3_x, -32767, 32767, -25, 25);
         //RLR = -mapValue(L3_x,-25,25);
         //LT = mapValue(R3_x, -25,25);
         LT = map(R3_x, -32767, 32767, -25, 25);

        
      
//      RFB = mapValue(movementArr[1], -50,50);
//      bounded_x_test_leg_string = String(RFB);
//      RLR = -mapValue(movementArr[0],-25,25);
//      bounded_y_test_leg_string = String(RLR);
//      LT = mapValue(movementArr[2], -25,25);
//      bounded_z_test_leg_string = String(LT);
//      RFB = 10;
//      RLR = 0;
//      LT = 0;
    
 
      RFBFiltered = filter(RFB, RFBFiltered, 15);
      RLRFiltered = filter(RLR, RLRFiltered, 15);
      LTFiltered = filter(LT, LTFiltered, 15);


      longLeg1 = 380;
      shortLeg1 = 320;
      longLeg2 = 380;
      shortLeg2 = 320;

      footOffset = 0;
      timer1 = 300;   // FB gait timer
      //timer2 = 75;   // LR gait timer
      //timer3 = 75;   // LR gait timer

      if (RFBFiltered > -0.1 && RFBFiltered < 0.1 && RLRFiltered > -0.1 && RLRFiltered < 0.1  && LTFiltered > -0.1 && LTFiltered < 0.1 ) {    // controls are centred or near enough

      
      // position legs a default standing positionS
          legLength1 = longLeg1;
          legLength2 = longLeg2;
          fr_RFB = 0;
          fl_RFB = 0;
          bl_RFB = 0;
          br_RFB = 0;
          fr_RLR = footOffset;
          fl_RLR = -footOffset;
          bl_RLR = -footOffset;
          br_RLR = footOffset;
          fr_LT = 0;
          fl_LT = 0;
          bl_LT = 0;
          br_LT = 0;        
      }
      
      //walking
      else {


          //Serial.println(timerScale);
        
          if (stepFlag == 0 && currentMillis - previousStepMillis > timerScale) {
              legLength1  = shortLeg1;
              legLength2 = longLeg2; 
              fr_RFB = 0-RFBFiltered;
              fl_RFB = RFBFiltered;
              bl_RFB = 0-RFBFiltered;
              br_RFB = RFBFiltered;
              fr_RLR = (footOffset -RLRFiltered) + LT;
              fl_RLR = (-footOffset +RLRFiltered) - LT;
              bl_RLR = (-footOffset - RLRFiltered) - LT;
              br_RLR = (footOffset + RLRFiltered) + LT;
              //fr_RLR = LT;
              //fl_RLR = 0-LT;
              //bl_RLR = 0-LT;
              //br_RLR = LT;
              stepFlag = 1;              
              previousStepMillis = currentMillis;
          }

          else if (stepFlag == 1 && currentMillis - previousStepMillis > timerScale) {
              legLength1 = longLeg1;
              legLength2 = longLeg2;
              fr_RFB = 0-RFBFiltered;
              fl_RFB = RFBFiltered;
              bl_RFB = 0-RFBFiltered;
              br_RFB = RFBFiltered;
              fr_RLR = (footOffset -RLRFiltered) + LT;
              fl_RLR = (-footOffset +RLRFiltered) - LT;
              bl_RLR = (-footOffset -RLRFiltered) - LT;
              br_RLR = (footOffset +RLRFiltered) + LT;
              //fr_RLR = LT;
              //fl_RLR = 0-LT;
              //bl_RLR = 0-LT;
              //br_RLR = LT;                        

              stepFlag = 2;              
              previousStepMillis = currentMillis;
          }

          else if (stepFlag == 2 && currentMillis - previousStepMillis > timerScale) {
              legLength1 = longLeg1;
              legLength2 = shortLeg2;
              fr_RFB = RFBFiltered;
              fl_RFB = 0-RFBFiltered;
              bl_RFB = RFBFiltered;
              br_RFB = 0-RFBFiltered;
              fr_RLR = (footOffset +RLRFiltered) - LT;
              fl_RLR = (-footOffset -RLRFiltered) + LT;
              bl_RLR = (-footOffset +RLRFiltered) + LT;
              br_RLR = (footOffset -RLRFiltered) - LT;
              //fr_RLR = 0-LT;
              //fl_RLR = LT;
              //bl_RLR = LT;
              // br_RLR = 0-LT; 
              stepFlag = 3;              
              previousStepMillis = currentMillis;
          }

          else if (stepFlag == 3 && currentMillis - previousStepMillis > timerScale) {
              legLength1 = longLeg1;
              legLength2 = longLeg2;
              fr_RFB = RFBFiltered;
              fl_RFB = 0-RFBFiltered;
              bl_RFB = RFBFiltered;
              br_RFB = 0-RFBFiltered;
              fr_RLR = (footOffset +RLRFiltered) - LT;
              fl_RLR = (-footOffset -RLRFiltered) + LT;
              bl_RLR = (-footOffset +RLRFiltered) + LT;
              br_RLR = (footOffset -RLRFiltered) - LT;
              //fr_RLR = 0-LT;
              //fl_RLR = LT;
              //bl_RLR = LT;
              //br_RLR = 0-LT; 
              stepFlag = 0;              
              previousStepMillis = currentMillis;
          }

           
          float stepLength;
          float stepWidth;
          float stepAngle;
          float stepHyp;

          // timer calcs

          stepLength = abs(fr_RFB);
          stepWidth = abs(fr_RLR);

          if (stepLength == 0.0) {
            stepLength = 0.01;   // avoid divide by zero
          }

          stepAngle = atan(stepLength/stepWidth);  // radians       // work out actual distance of step
          stepHyp = abs(stepLength/sin(stepAngle));    // mm

          timerScale =  timer1 + (stepHyp/3.5);         
          
      }
    
      
      //Gyro section:
      gyro_signals();
      RateRoll-=RateCalibrationRoll;
      RatePitch-=RateCalibrationPitch;
      RateYaw-=RateCalibrationYaw;
      kalman_1d(KalmanAngleRoll, KalmanUncertaintyAngleRoll, RateRoll, AngleRoll);
      KalmanAngleRoll=Kalman1DOutput[0]; 
      KalmanUncertaintyAngleRoll=Kalman1DOutput[1];
      kalman_1d(KalmanAnglePitch, KalmanUncertaintyAnglePitch, RatePitch, AnglePitch);
      KalmanAnglePitch=Kalman1DOutput[0]; 
      KalmanUncertaintyAnglePitch=Kalman1DOutput[1];
      
      
      fr_RFB_string = String(fr_RFB);
      fr_RLR_string = String(fr_RLR);
      legLength1_string = String(legLength1);
      LegRollFiltered = filter(KalmanAngleRoll,LegRollFiltered,5);
      LegPitchFiltered = filter(KalmanAnglePitch,LegPitchFiltered,5);
      
      kinematics (1, fr_RFB, fr_RLR, legLength1, -1*LegRollFiltered, LegPitchFiltered, 0, 1, (timerScale*0.8));   // front right
      kinematics (2, fl_RFB, fl_RLR, legLength2, -1*LegRollFiltered, LegPitchFiltered, 0, 1, (timerScale*0.8));   // front left
      kinematics (3, bl_RFB, bl_RLR, legLength1, -1*LegRollFiltered, LegPitchFiltered, 0, 1, (timerScale*0.8));   // back left
      kinematics (4, br_RFB, br_RLR, legLength2, -1*LegRollFiltered, LegPitchFiltered, 0, 1, (timerScale*0.8));   // back right 
    }
//    else{
//      kinematics (1, fr_RFB, fr_RLR, legLength1, 1*KalmanAngleRoll, /*KalmanAnglePitch*/0, 0, 1, (timerScale*0.8));   // front right
//      kinematics (2, fl_RFB, fl_RLR, legLength2, 1*KalmanAngleRoll, /*KalmanAnglePitch*/0, 0, 1, (timerScale*0.8));   // front left
//      kinematics (3, bl_RFB, bl_RLR, legLength1, 1*KalmanAngleRoll, /*KalmanAnglePitch*/0, 0, 1, (timerScale*0.8));   // back left
//      kinematics (4, br_RFB, br_RLR, legLength2, 1*KalmanAngleRoll, /*KalmanAnglePitch*/0, 0, 1, (timerScale*0.8));   // back right 
//    }
  }
  //updateMovement();
  
