#include <Wire.h>
const int MPU = 0x68; // MPU6050 I2C address
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;
float AccX_old, AccY_old, AccZ_old;
float GyroX_old, GyroY_old, GyroZ_old;
float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
float roll, pitch, yaw;
float elapsedTime, currentTime, previousTime;

void setup() {
  Serial.begin(115200);
  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  delay(10);
  
}
void loop() {
  // === Read acceleromter data === //
  Wire.beginTransmission(MPU);
  Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
  //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
  AccX = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
  AccY = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
  AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value
  
  // === Read gyroscope data === //
  previousTime = currentTime;        // Previous time is stored before the actual time read
  currentTime = millis();            // Current time actual time read
  elapsedTime = (currentTime - previousTime) / 1000; // Divide by 1000 to get seconds
  Wire.beginTransmission(MPU);
  Wire.write(0x43); // Gyro data first register address 0x43
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 4 registers total, each axis value is stored in 2 registers
  GyroX = (Wire.read() << 8 | Wire.read()) / 131; // For a 1000deg/s range we have to divide first the raw value by 32.8, according to the datasheet
  GyroY = (Wire.read() << 8 | Wire.read()) / 131;
  GyroZ = (Wire.read() << 8 | Wire.read()) / 131;
//Compensate for sign offset
  GyroX = GyroX+2;
  if (GyroX > 250){
    GyroX = -500 + GyroX;
  }
  GyroY = GyroY+1;
  if (GyroY > 250){
    GyroY = -500 + GyroY;
  }
  if (GyroZ > 250){
    GyroZ = -500 + GyroZ;
  }
  if (AccX > 2){
    AccX = AccX-4;
  }
  if (AccY > 2){
    AccY = AccY-4;
  }
  if (AccZ > 2){
    AccZ = AccZ-4;
  }

  //for roll pitch and yaw
  accAngleX = (atan(AccY / sqrt(pow(AccX, 2) + pow(AccZ, 2))) * 180 / PI); 
  accAngleY = (atan(-1 * AccX / sqrt(pow(AccY, 2) + pow(AccZ, 2))) * 180 / PI);
  // Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by sendonds (s) to get the angle in degrees
  gyroAngleX = gyroAngleX + GyroX * elapsedTime; // deg/s * s = deg
  gyroAngleY = gyroAngleY + GyroY * elapsedTime;
  yaw =  yaw + GyroZ * elapsedTime;

  roll = 0.96 * gyroAngleY + 0.04 * accAngleY;
  pitch = 0.96 * gyroAngleX + 0.04 * accAngleX; 
  
  // Print the values on the serial monitor
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
//  Serial.print(AccZ);
//  Serial.print(" GyroX: ");
//  Serial.print(GyroX);
//  Serial.print(" GyroY: ");
//  Serial.println(GyroY);
//  Serial.print(" GyroZ: ");
//  Serial.println(GyroZ);

}
