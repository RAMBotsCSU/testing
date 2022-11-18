#include "Wire.h"
#include "I2Cdev.h"
#include "MPU6050.h"

//pin 19 is SCL on Teenssy 4.1
//pin 18 is SDA on Teenssy 4.1
//connect to 3V line on teensy(its pin 
MPU6050 accelgyro;
int16_t ax, ay, az;
int16_t gx, gy, gz;

#define Gyr_Gain 0.00763358 

float AccelX;
float AccelY;
float AccelZ;

float GyroX;
float GyroY;
float GyroZ;

float mixX;
float mixY;

float pitchAccel, rollAccel;

float IMUpitch;
float IMUroll;

void setup() {
   Serial.begin(115200);
   delay(10);
   Serial.print("Starting\n");
}

boolean on=1;

void loop() {
  
  if (on == 1) {
          // read IMU
          Wire.begin();   
          accelgyro.initialize(); 
          accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
          
          AccelX = ax;
          AccelY = ay;
          AccelZ = az;
          GyroX = Gyr_Gain * (gx);
          GyroY = Gyr_Gain * (gy)*-1;
          GyroZ = Gyr_Gain * (gz);
        
          AccelY = (atan2(AccelY, AccelZ) * 180 / PI);
          AccelX = (atan2(AccelX, AccelZ) * 180 / PI);
      
          float dt = 0.01;
          float K = 0.9;
          float A = K / (K + dt);
        
          mixX = A *(mixX+GyroX*dt) + (1-A)*AccelY;    
          mixY = A *(mixY+GyroY*dt) + (1-A)*AccelX; 
      
          IMUpitch = mixX + 2.7;      // trim IMU to zero
          IMUroll = mixY - 5;     
          
          
//           Serial.print("ax: ");
//           Serial.print(ax);
//           Serial.print(" ay: ");
//           Serial.print(ay);
//           Serial.print(" az: ");
//           Serial.println(az);
          
           Serial.print("gx: ");
           Serial.print(gx);
           Serial.print(" gy: ");
           Serial.print(gy);
           Serial.print(" gz: ");
           Serial.println(gz);
          
          
          Wire.end();
          delay(10);
      }
      else {
          // ignore IMU data
          Wire.end();
          IMUpitch = 0;      // IMU data is zeero, do not read IMU 
          IMUroll = 0;
      }
      if(on==0){on==1;delay(100);}
      
    //for adjusting motor positions with gyroscope
    // legTransX = IMUpitch * -2;
    // legTransY = IMUroll * -2;

    // legTransXFiltered = filter(legTransX,legTransXFiltered,50);
    // legTransYFiltered = filter(legTransY,legTransYFiltered,50);

    // legRoll = IMUroll * -0.5;
    // legPitch = IMUpitch * 0.5;

    // legRollFiltered = filter(legRoll,legRollFiltered,60);
    // legPitchFiltered = filter(legPitch,legPitchFiltered,60);
    
}
