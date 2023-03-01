double black,blue,green,yellow,grey,red;
double high_threshold = 1000.0;
double low_threshold = 15.0;
void setup() {
  //Teensy connections
  //Digital pins:
  // connect black to pin 5
  //blue to pin 6
  //yellow to pin 7
  //green to pin 8
  //grey to pin 9
  //red to pin 10

  //Analog reading pins:
  //black to pin 20
  //black to pin 19
  //black to pin 18
  //black to pin 17
  //black to pin 16
  //black to pin 15

}

void loop() {
  // put your main code here, to run repeatedly:
digitalWrite(5, HIGH);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(black>high_threshold && blue<low_threshold && yellow<low_threshold && green<low_threshold && grey<low_threshold && red<low_threshold){
  Serial.print(" black: Pass");
}else{
  Serial.print(" black: !Fail!");
  Dumpinfo();
}
digitalWrite(5, LOW);
digitalWrite(6, HIGH);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(blue>high_threshold && black<low_threshold && yellow<low_threshold && green<low_threshold && grey<low_threshold && red<low_threshold){
  Serial.print(" blue: Pass");
}else{
  Serial.print(" blue: !Fail!");
  Dumpinfo();
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, HIGH);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(yellow>high_threshold && black<low_threshold && blue<low_threshold && green<low_threshold && grey<low_threshold && red<low_threshold){
  Serial.print(" yellow: Pass");
}else{
  Serial.print(" yellow: !Fail!");
  Dumpinfo();
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, HIGH);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(green>high_threshold && black<low_threshold && blue<low_threshold && yellow<low_threshold && grey<low_threshold && red<low_threshold){
  Serial.print(" green: Pass");
}else{
  Serial.print(" green: !Fail!");
  Dumpinfo();
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, HIGH);
digitalWrite(10, LOW);
delay(5);
Read();
if(grey>high_threshold && black<low_threshold && blue<low_threshold && yellow<low_threshold && green<low_threshold && red<low_threshold){
  Serial.print(" grey: Pass");
}else{
  Serial.print(" grey: !Fail!");
  Dumpinfo();
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, HIGH);
delay(5);
Read();
if(red>high_threshold && black<low_threshold && blue<low_threshold && yellow<low_threshold && green<low_threshold && grey<low_threshold){
  Serial.println(" red: Pass");
}else{
  Serial.println(" red: !Fail!");
  Dumpinfo();
}
}
void Read() {

black = analogRead(A6);
blue = analogRead(A5);
yellow = analogRead(A4);
green = analogRead(A3);
grey = analogRead(A2);
red = analogRead(A1);
delay(10);
}
void Dumpinfo() {

  Serial.println();
Serial.print(" black:");
Serial.print(black);
Serial.print(" blue:");
Serial.print(blue);
Serial.print(" yellow:");
Serial.print(yellow);
Serial.print(" green:");
Serial.print(green);
Serial.print(" grey:");
Serial.print(grey);
Serial.print(" red:");
Serial.println(red);
delay(5);
}
