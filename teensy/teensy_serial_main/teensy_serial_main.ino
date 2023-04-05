//********************************************************************************
//* This program creates a movement array of the format                          *
//* [strafe, forback, roll, turn, pitch, height, yaw] and maintains it           *
//* using serial messages from the Pi. Included in these messages are            *
//* different modes of operation that will result in different program           *
//* behavior. Depending on the selected mode, the Teensy will translate          *
//* the movement array into o-drive movement via the kinematics function         *
//* created by James Bruton.                                                     *
//*                                                                              *
//* ODriveInit initializes the o-drives with offsets specific to the Rambot.     *
//*                                                                              *
//* Kinematics_Helper_Suite provides an alternative interpolation method         *
//* to James Bruton's.                                                           *
//********************************************************************************

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
int setNum = 1;

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

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  odrive1Serial.begin(115200);
  odrive2Serial.begin(115200);
  odrive3Serial.begin(115200);
  odrive4Serial.begin(115200);
  odrive5Serial.begin(115200);
  odrive6Serial.begin(115200);
  //Serial7.begin(115200);

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

// should probably be using map() instead
float mapValue(float val, float lower_range, float upper_range){ // map joystick range [-1,1] to [lower,upper]
    float normalizedValue = (val + 1.00) / 2.00;
    return lower_range + (normalizedValue * (upper_range - lower_range));
}

int keyword_to_int(String keyWord){ // convert 2 character keyword to an int value to use switch statements
    return (keyWord[0] - '0') * 10 + (keyWord[1] - '0');
}


//Main loop to be executed
void loop() {

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

          Serial.println(padStr("x: " + bounded_x_test_leg_string + " y: " + bounded_y_test_leg_string + " z: " + bounded_z_test_leg_string));      //Print to the serial buffer  
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
    case 0:  //normal walking (ps4 control)
//      fullWalk(movementArr, 1.0, setNum);
      //if all of the movment array numbers are 0, next stage needs to be 1, unless we are going down, then do it next time
      if(setNum == 5){
        setNum = 2;
      }
//      else if(/*if stopping*/){
//        setNum = 6;
//      }
      else if(setNum = 6){
        setNum = 1;
      }
      else{
        setNum ++;
      }
      break;
    case 1:   // movementArr[1] = 
    //  transitionKinematics(bounded_x_test_leg, mapValue(arr[1],-100,100), bounded_y_test_leg, mapValue(arr[2],-100,100), 0, 0)
        bounded_x_test_leg = mapValue(movementArr[1],-300,300);
        bounded_x_test_leg_string = String(bounded_x_test_leg);
        bounded_y_test_leg = -mapValue(movementArr[0],-100,100);
        bounded_y_test_leg_string = String(bounded_y_test_leg);
        bounded_z_test_leg = bounded_z_test_leg + (350+240)/2 * 0.2 *movementArr[5];
        if (bounded_z_test_leg > 350){
          bounded_z_test_leg = 350;
        }
        else if (bounded_z_test_leg < 240){
          bounded_z_test_leg = 240;
        }
        bounded_z_test_leg_string = String(bounded_z_test_leg);
        kinematics(1,bounded_x_test_leg,bounded_y_test_leg,bounded_z_test_leg,0,0,0,0,0);
        kinematics(4,bounded_x_test_leg,bounded_y_test_leg,bounded_z_test_leg,0,0,0,0,0);
//        ztop =240
//        zbot = 350
//        transkine(x_BIG_VARIABLE,transfunction(arr[1],bounds,yfrom,yto,zfrom,zto
//        x_BIG = transfunction(arr[1],bounds)
//        y_big
//        z_big = z_big+((ztop+zbot)/2*0.01*arr[z])
      
      break;

  
 



  }
}
