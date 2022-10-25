int led = 13;
void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
}

String padStr(String str){
  int target = 120-str.length();
  for (int i = 0; i < target; i++) {
    str += "~";
  }
  return str;
}

String rmPadStr(String str){
  for (int i = 0; i < str.length(); i++){
    if (str[i] == '~'){
//      Serial.println("Found padding starting at index: " + i);
      str.remove(i);
      return str;
    }
  }
}

void loop() {
  //Serial.println("Enter data:");
  //while (Serial.available() == 0) {}     //wait for data available
  digitalWrite(led, LOW);   // turn the LED on (HIGH is the voltage level)
  String readStr = Serial.readString();  //read until timeout
  readStr.trim();                        // remove any \r \n whitespace at the end of the String
  //readStr = rmPadStr(readStr);
  if (!(readStr == "")){
    digitalWrite(led, HIGH);    // turn the LED off by making the voltage LOW
    readStr = ("Button Pressed. I got: " + readStr);
    //readStr = padStr(readStr);
    Serial.println(readStr);
  }
//  testPadding();
}
