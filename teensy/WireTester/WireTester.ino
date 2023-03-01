double black,blue,green,yellow,grey,red;
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
if(black>1000 && blue<15 && yellow<15 && green<15 && grey<15 && red<15){
  Serial.print(" black: Pass");
}else{
  Serial.print(" black: !Fail!");
}
digitalWrite(5, LOW);
digitalWrite(6, HIGH);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(blue>1000 && black<15 && yellow<15 && green<15 && grey<15 && red<15){
  Serial.print(" blue: Pass");
}else{
  Serial.print(" blue: !Fail!");
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, HIGH);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(yellow>1000 && black<15 && blue<15 && green<15 && grey<15 && red<15){
  Serial.print(" yellow: Pass");
}else{
  Serial.print(" yellow: !Fail!");
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, HIGH);
digitalWrite(9, LOW);
digitalWrite(10, LOW);
delay(5);
Read();
if(green>1000 && black<15 && blue<15 && yellow<15 && grey<15 && red<15){
  Serial.print(" green: Pass");
}else{
  Serial.print(" green: !Fail!");
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, HIGH);
digitalWrite(10, LOW);
delay(5);
Read();
if(grey>1000 && black<15 && blue<15 && yellow<15 && green<15 && red<15){
  Serial.print(" grey: Pass");
}else{
  Serial.print(" grey: !Fail!");
}
digitalWrite(5, LOW);
digitalWrite(6, LOW);
digitalWrite(7, LOW);
digitalWrite(8, LOW);
digitalWrite(9, LOW);
digitalWrite(10, HIGH);
delay(5);
Read();
if(red>1000 && black<15 && blue<15 && yellow<15 && green<15 && grey<15){
  Serial.println(" red: Pass");
}else{
  Serial.println(" red: !Fail!");
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


//Serial.print(" black:");
//Serial.print(black);
//Serial.print(" blue:");
//Serial.print(blue);
//Serial.print(" yellow:");
//Serial.print(yellow);
//Serial.print(" green:");
//Serial.print(green);
//Serial.print(" grey:");
//Serial.print(grey);
//Serial.print(" red:");
//Serial.println(red);
//delay(100);

}
