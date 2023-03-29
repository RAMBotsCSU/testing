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

ODriveArduino odrArr[6] = {odrive1, odrive2, odrive3, odrive4, odrive5, odrive6};

#include <Wire.h>
const int MPU = 0x68; // MPU6050 I2C address 0x68 for first mpu 0x69 for second
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;
float AccX_old, AccY_old, AccZ_old;
float GyroX_old, GyroY_old, GyroZ_old;
float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
float roll, pitch, yaw;
String roll_string, pitch_string, yaw_string;
float elapsedTime, currentTime, previousTime;

int c =0;
float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;


void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  odrive1Serial.begin(115200);
  odrive2Serial.begin(115200);
  odrive3Serial.begin(115200);
  odrive4Serial.begin(115200);
  odrive5Serial.begin(115200);
  odrive6Serial.begin(115200);

  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  calculate_IMU_error();
  
  delay(10);
  
  //Serial7.begin(115200);

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


//Main loop to be executed
void loop() {

   Wire.beginTransmission(MPU);
  Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
  //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
  AccX = TwosComp(Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
  AccY = TwosComp(Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
  AccZ = TwosComp(Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value
  
  //apply offsets
  AccX = AccX - AccErrorX;
  AccY = AccY - AccErrorY;
//  AccZ = AccZ - AccErrorZ;
  
  // === Read gyroscope data === //
  
  Wire.beginTransmission(MPU);
  Wire.write(0x43); // Gyro data first register address 0x43
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 4 registers total, each axis value is stored in 2 registers
  GyroX = TwosComp(Wire.read() << 8 | Wire.read()) / 131; // For a 1000deg/s range we have to divide first the raw value by 32.8, according to the datasheet
  GyroY = TwosComp(Wire.read() << 8 | Wire.read()) / 131;
  GyroZ = TwosComp(Wire.read() << 8 | Wire.read()) / 131;

  //apply ofsets
  GyroX = GyroX - GyroErrorX;
  GyroY = GyroY - GyroErrorY;
  GyroZ = GyroZ - GyroErrorZ;
//  GyroX = GyroX+5.5;
//  GyroY = GyroY+1;
//  GyroZ = GyroZ;
  
  //for roll pitch and yaw
  accAngleX = (atan(AccY / sqrt(pow(AccX, 2) + pow(AccZ, 2))) * 180 / PI); 
  accAngleY = (atan(-1 * AccX / sqrt(pow(AccY, 2) + pow(AccZ, 2))) * 180 / PI);
  // Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by sendonds (s) to get the angle in degrees
  previousTime = currentTime;        // Previous time is stored before the actual time read
  currentTime = millis();            // Current time actual time read
  elapsedTime = (currentTime - previousTime) / 1000; // Divide by 1000 to get seconds
  
  gyroAngleX = gyroAngleX + GyroX * elapsedTime; // deg/s * s = deg
  gyroAngleY = gyroAngleY + GyroY * elapsedTime;
  yaw =  yaw + GyroZ * elapsedTime;

  roll = roll + GyroY * elapsedTime;
  pitch = pitch + GyroX * elapsedTime; 









  
  digitalWrite(led, LOW);                             //Set LED to off when no message has been recieved
  //while (Serial.available() == 0) {}                //optional wait for serial input
  String readStr = Serial.readString();               //Read the serial line and set to readStr
  readStr.trim();                                     //Remove any \r \n whitespace at the end of the String
  readStr = rmPadStr(readStr);                        //Remove any padding from readStr
  if (readStr != ""){                                 //readStr == "" if the serial read had nothing in it
    digitalWrite(led, HIGH);                          //Turn on the LED to show that a string with != "" has been recieved
    keyWord = readStr.substring(0,2);
    switch(keyword_to_int(keyWord)) { // convert to int so we can use speedy switch statements
      case 204: // keyword_to_int("AR")
        setInd = (readStr.substring(readStr.indexOf("R")+1,readStr.indexOf(":"))).toInt();
        setVal = (readStr.substring(readStr.indexOf(":")+1,readStr.indexOf(","))).toFloat();
        movementArr[setInd] = setVal;
        if (currentMode == 1){
          //moving index to transvalue

          Serial.println(padStr("x: " + bounded_x_test_leg_string + " y: " + bounded_y_test_leg_string + " z: " + bounded_z_test_leg_string) + " pitch: " + pitch_string + " roll: " + roll_string + " yaw: " + yaw_string);      //Print to the serial buffer  
        } 
        else if (currentMode == 2){
          Serial.println(" roll: " + String(roll));
        }
        
        else
          Serial.println(padStr(getArrStr()));      //Print to the serial buffer
        break;
      case 383: // keyword_to_int("SQ")
        testMovement();
        Serial.println(padStr("Test Complete"));
        break;
      case 259: // keyword_to_int("GM")
        //applyOffsets1();
        //applyOffsets2();
        modifyGains();
        Serial.println(padStr("Gain Mode Set"));
        break;
      case 389: // keyword_to_int("TM") 
        Serial.println(padStr("Terminate"));
        while(1); // forever loop (halt teensy until reset)
        break;
      case 325: // keyword_to_int("MS") 
        currentMode = readStr.substring(readStr.indexOf(":")+1,readStr.indexOf(":")+2).toInt();
        currentModeString = String(currentMode);
        Serial.println(padStr("Mode Select:" + currentModeString));
        break;
      default:
        Serial.println(padStr("Unknown command: " + keyWord));
        break;
    }
  }
 switch(currentMode){
    case 0:           
      break;
    case 1:   // movementArr[1] = 
    //  transitionKinematics(bounded_x_test_leg, mapValue(arr[1],-100,100), bounded_y_test_leg, mapValue(arr[2],-100,100), 0, 0)
        bounded_x_test_leg = mapValue(movementArr[1],-300,300);
        bounded_x_test_leg_string = String(bounded_x_test_leg);
        bounded_y_test_leg = -mapValue(movementArr[0],-100,100);
        bounded_y_test_leg_string = String(bounded_y_test_leg);
        pitch_string = String(pitch);      
        roll_string = String(roll);      
        yaw_string = String(yaw);      

        bounded_z_test_leg = bounded_z_test_leg + (350+240)/2 * 0.2 *movementArr[5];
        if (bounded_z_test_leg > 350){
          bounded_z_test_leg = 350;
        }
        else if (bounded_z_test_leg < 240){
          bounded_z_test_leg = 240;
        }
        bounded_z_test_leg_string = String(bounded_z_test_leg);
        kinematics(1,bounded_x_test_leg,bounded_y_test_leg,bounded_z_test_leg,0,0,0,0,0);
//        ztop =240
//        zbot = 350
//        transkine(x_BIG_VARIABLE,transfunction(arr[1],bounds,yfrom,yto,zfrom,zto
//        x_BIG = transfunction(arr[1],bounds)
//        y_big
//        z_big = z_big+((ztop+zbot)/2*0.01*arr[z])
      
      break;


  
 



  }
  //updateMovement();
  }





float TwosComp(short bin){
  if(1 == bin>>15)
  {
    return ~bin +1;
  }
  return bin;
}
void calculate_IMU_error() {
  // We can call this funtion in the setup section to calculate the accelerometer and gyro data error. From here we will get the error values used in the above equations printed on the Serial Monitor.
  // Note that we should place the IMU flat in order to get the proper values, so that we then can the correct values
  // Read accelerometer values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    AccX = TwosComp(Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccY = TwosComp(Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccZ = TwosComp(Wire.read() << 8 | Wire.read()) / 16384.0 ;
    // Sum all readings
    AccErrorX = AccErrorX + ((atan((AccY) / sqrt(pow((AccX), 2) + pow((AccZ), 2))) * 180 / PI));
    AccErrorY = AccErrorY + ((atan(-1 * (AccX) / sqrt(pow((AccY), 2) + pow((AccZ), 2))) * 180 / PI));
    c++;
  }
  //Divide the sum by 200 to get the error value
  AccErrorX = AccErrorX / 200;
  AccErrorY = AccErrorY / 200;
  c = 0;
  // Read gyro values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x43);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    GyroX = TwosComp(Wire.read() << 8 | Wire.read());
    GyroY = TwosComp(Wire.read() << 8 | Wire.read());
    GyroZ = TwosComp(Wire.read() << 8 | Wire.read());
    // Sum all readings
    GyroErrorX = GyroErrorX + (GyroX / 131.0);
    GyroErrorY = GyroErrorY + (GyroY / 131.0);
    GyroErrorZ = GyroErrorZ + (GyroZ / 131.0);
    c++;
  }
  //Divide the sum by 200 to get the error value
  GyroErrorX = GyroErrorX / 200;
  GyroErrorY = GyroErrorY / 200;
  GyroErrorZ = GyroErrorZ / 200;

}
