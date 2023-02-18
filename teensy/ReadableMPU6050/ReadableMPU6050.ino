//TO DO:
//Correct Roll Pitch and Yaw values
//maybe add error correction with a running sum

#include <Wire.h>
const int MPU = 0x69; // MPU6050 I2C address
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;
float AccX_old, AccY_old, AccZ_old;
float GyroX_old, GyroY_old, GyroZ_old;
float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
float roll, pitch, yaw;
float elapsedTime, currentTime, previousTime;

int c =0;
float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;

void setup() {
  Serial.begin(115200);
  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  calculate_IMU_error();
  
  delay(10);
  
}
void loop() {
  // === Read acceleromter data === //
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
  
  // Print the values on the serial monitor
  Serial.print("0:");
  Serial.print(0);
  Serial.print(" Yaw: ");
  Serial.print(yaw);
  Serial.print(" pitch: ");
  Serial.print(pitch);
  Serial.print(" roll: ");
  Serial.println(roll);

//  Serial.print(" AccX: ");
//  Serial.print(AccX);
//  Serial.print(" AccY: ");
//  Serial.print(AccY);
//  Serial.print(" AccZ: ");
//  Serial.println(AccZ);
//  Serial.print(" GyroX: ");
//  Serial.print(GyroX);
//  Serial.print(" GyroY: ");
//  Serial.print(GyroY);
//  Serial.print(" GyroZ: ");
//  Serial.println(GyroZ);

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
  // Print the error values on the Serial Monitor
//  Serial.print("AccErrorX: ");
//  Serial.println(AccErrorX);
//  Serial.print("AccErrorY: ");
//  Serial.println(AccErrorY);
//  Serial.print("GyroErrorX: ");
//  Serial.println(GyroErrorX);
//  Serial.print("GyroErrorY: ");
//  Serial.println(GyroErrorY);
//  Serial.print("GyroErrorZ: ");
//  Serial.println(GyroErrorZ);
}
