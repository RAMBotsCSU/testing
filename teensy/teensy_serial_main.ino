//********************************************************
//* This is a simple test for the teensy that recieves   *
//* a string over the serial line, appends some values   *
//* then sends it back over serial. This method includes *
//* padding functions for the serial communication to    *
//* speed up the communication.                          *
//********************************************************

//Setup and set the pin for the LED
int led = 13;
void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
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
    readStr = ("Button Pressed. I got: " + readStr);  //Append a message to the string
    readStr = padStr(readStr);                        //Add padding to the string
    Serial.println(readStr);                          //Print to the serial buffer
  }
}
