//********************************************************
//* This is a simple test for the teensy that recieves   *
//* a string over the serial line, appends some values   *
//* then sends it back over serial. This method includes *
//* padding functions for the serial communication to    *
//* speed up the communication.                          *
//********************************************************

//Setup and set the pin for the LED
int led = 13;
int setInd = -1;
float setVal = -1.1;
float movementArr[7]; //0 = strafe, 1 = forback, 2 = roll, 3 = turn, 4 = pitch, 5 = height, 6 = yaw
String keyWord = "00";

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
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
    if (keyWord == "AR"){
      setInd = (readStr.substring(readStr.indexOf("R")+1,readStr.indexOf(":"))).toInt();
      setVal = (readStr.substring(readStr.indexOf(":")+1,readStr.indexOf(","))).toFloat();
      movementArr[setInd] = setVal;
      Serial.println(getArrStr());      //Print to the serial buffer
    }
  }
}
