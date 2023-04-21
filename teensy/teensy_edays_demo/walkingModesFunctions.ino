
float RLR = 0;
float RFB = 0;
float LT = 0;

float longLeg1;
float shortLeg1;
float legLength1;
float longLeg2;
float shortLeg2;
float legLength2;
float footOffset;

int timer1;   // FB gait timer
int timer2;   // LR gait timer
int timer3;   // Yaw gait timer
float timerScale;   // resulting timer after calcs
float timerScale2;   // multiplier

float RLRFiltered = 0;
float RFBFiltered = 0;
float RTFiltered = 340;
float LLRFiltered = 0;
float LFBFiltered = 0;
float LTFiltered = 0;
int filterFlag1 = 0;

float Roll = 0;
float Pitch = 0;


int stepFlag = 0;
long previousStepMillis = 0;
int stepStartFlag = 0;

float fr_RFB;
float fl_RFB;
float bl_RFB;
float br_RFB;
float fr_RLR;
float fl_RLR;
float bl_RLR;
float br_RLR;
float fr_LT;
float fl_LT;
float bl_LT;
float br_LT;

//update gyro variables
//gyro update call
void updateGyro(){
      gyro_signals();
      RateRoll-=RateCalibrationRoll;
      RatePitch-=RateCalibrationPitch;
      RateYaw-=RateCalibrationYaw;
      kalman_1d(KalmanAngleRoll, KalmanUncertaintyAngleRoll, RateRoll, AngleRoll);
      KalmanAngleRoll=Kalman1DOutput[0]; 
      KalmanUncertaintyAngleRoll=Kalman1DOutput[1];
      kalman_1d(KalmanAnglePitch, KalmanUncertaintyAnglePitch, RatePitch, AnglePitch);
      KalmanAnglePitch=Kalman1DOutput[0]; 
      KalmanUncertaintyAnglePitch=Kalman1DOutput[1];
            
      LegRollFiltered = filter(KalmanAngleRoll,LegRollFiltered,5);
      LegPitchFiltered = filter(KalmanAnglePitch,LegPitchFiltered,5);
}

void kalman_1d(float KalmanState, float KalmanUncertainty, float KalmanInput, float KalmanMeasurement) {
  KalmanState=KalmanState+0.004*KalmanInput;
  KalmanUncertainty=KalmanUncertainty + 0.004 * 0.004 * 4 * 4;
  float KalmanGain=KalmanUncertainty * 1/(1*KalmanUncertainty + 3 * 3);
  KalmanState=KalmanState+KalmanGain * (KalmanMeasurement-KalmanState);
  KalmanUncertainty=(1-KalmanGain) * KalmanUncertainty;
  Kalman1DOutput[0]=KalmanState; 
  Kalman1DOutput[1]=KalmanUncertainty;
}

void gyro_signals(void) {
  Wire.beginTransmission(0x68);
  Wire.write(0x1A);
  Wire.write(0x05);
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x10);
  Wire.endTransmission();
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission(); 
  Wire.requestFrom(0x68,6);
  int16_t AccXLSB = Wire.read() << 8 | Wire.read();
  int16_t AccYLSB = Wire.read() << 8 | Wire.read();
  int16_t AccZLSB = Wire.read() << 8 | Wire.read();
  Wire.beginTransmission(0x68);
  Wire.write(0x1B); 
  Wire.write(0x8);
  Wire.endTransmission();     
  Wire.beginTransmission(0x68);
  Wire.write(0x43);
  Wire.endTransmission();
  Wire.requestFrom(0x68,6);
  int16_t GyroX=Wire.read()<<8 | Wire.read();
  int16_t GyroY=Wire.read()<<8 | Wire.read();
  int16_t GyroZ=Wire.read()<<8 | Wire.read();
  RateRoll=(float)GyroX/65.5;
  RatePitch=(float)GyroY/65.5;
  RateYaw=(float)GyroZ/65.5;
  AccX=(float)AccXLSB/4096;
  AccY=(float)AccYLSB/4096;
  AccZ=(float)AccZLSB/4096;
  AngleRoll=atan(AccY/sqrt(AccX*AccX+AccZ*AccZ))*1/(3.142/180);
  AnglePitch=-atan(AccX/sqrt(AccY*AccY+AccZ*AccZ))*1/(3.142/180);
}


// advance opendog walk cycle
void openDogWalkCycle(float forward_backward, float turn, float strafe, float look_up, float look_down, bool gyro){
    RFB = map(forward_backward, -1, 1, -50, 50);
    RLR = -1*map(-turn, -1, 1, -25, 25);
    LT = map(strafe, -1, 1, -25, 25);

    //offset to account for the dogs natural rotation
/*  if(RFB != 0){
      LT = (LT+(0.5*RFB); //if its linearly dependant of the FB sspeed TODO: find the constant
    }*/
  // most code below is straight from from opendogV3: 

    RFBFiltered = filter(RFB, RFBFiltered, 15);
    RLRFiltered = filter(RLR, RLRFiltered, 15);
    LTFiltered = filter(LT, LTFiltered, 15);
  
    //previously 380 and 320
    longLeg1 = maxLegHeight;
    shortLeg1 = minLegHeight;
    longLeg2 = maxLegHeight;
    shortLeg2 = minLegHeight;
  
    footOffset = 0;
    timer1 = 75;   // FB gait timer -- this changes step speed (default 75)
    //timer2 = 75;   // LR gait timer
    //timer3 = 75;   // LR gait timer
  
    if (RFBFiltered > -0.1 && RFBFiltered < 0.1 && RLRFiltered > -0.1 && RLRFiltered < 0.1  && LTFiltered > -0.1 && LTFiltered < 0.1 ) {    // controls are centred or near enough
  
    
    // position legs a default standing positionS
        legLength1 = longLeg1;
        legLength2 = longLeg2;
        fr_RFB = 0;
        fl_RFB = 0;
        bl_RFB = 0;
        br_RFB = 0;
        fr_RLR = footOffset;
        fl_RLR = -footOffset;
        bl_RLR = -footOffset;
        br_RLR = footOffset;
        fr_LT = 0;
        fl_LT = 0;
        bl_LT = 0;
        br_LT = 0; 

        //look_up_or_down(look_up,  look_down);
        //return;
               
    }
    
    //walking
    else {
      //Serial.println(timerScale);
        if (stepFlag == 0 && currentMillis - previousStepMillis > timerScale) {
            legLength1  = shortLeg1;
            legLength2 = longLeg2; 
            fr_RFB = 0-RFBFiltered;
            fl_RFB = RFBFiltered;
            bl_RFB = 0-RFBFiltered;
            br_RFB = RFBFiltered;
            fr_RLR = (footOffset -RLRFiltered) + LT;
            fl_RLR = (-footOffset +RLRFiltered) - LT;
            bl_RLR = (-footOffset - RLRFiltered) - LT;
            br_RLR = (footOffset + RLRFiltered) + LT;
            //fr_RLR = LT;
            //fl_RLR = 0-LT;
            //bl_RLR = 0-LT;
            //br_RLR = LT;
            stepFlag = 1;              
            previousStepMillis = currentMillis;
        }
  
        else if (stepFlag == 1 && currentMillis - previousStepMillis > timerScale) {
            legLength1 = longLeg1;
            legLength2 = longLeg2;
            fr_RFB = 0-RFBFiltered;
            fl_RFB = RFBFiltered;
            bl_RFB = 0-RFBFiltered;
            br_RFB = RFBFiltered;
            fr_RLR = (footOffset -RLRFiltered) + LT;
            fl_RLR = (-footOffset +RLRFiltered) - LT;
            bl_RLR = (-footOffset -RLRFiltered) - LT;
            br_RLR = (footOffset +RLRFiltered) + LT;
            //fr_RLR = LT;
            //fl_RLR = 0-LT;
            //bl_RLR = 0-LT;
            //br_RLR = LT;                        
  
            stepFlag = 2;              
            previousStepMillis = currentMillis;
        }
  
        else if (stepFlag == 2 && currentMillis - previousStepMillis > timerScale) {
            legLength1 = longLeg1;
            legLength2 = shortLeg2;
            fr_RFB = RFBFiltered;
            fl_RFB = 0-RFBFiltered;
            bl_RFB = RFBFiltered;
            br_RFB = 0-RFBFiltered;
            fr_RLR = (footOffset +RLRFiltered) - LT;
            fl_RLR = (-footOffset -RLRFiltered) + LT;
            bl_RLR = (-footOffset +RLRFiltered) + LT;
            br_RLR = (footOffset -RLRFiltered) - LT;
            //fr_RLR = 0-LT;
            //fl_RLR = LT;
            //bl_RLR = LT;
            // br_RLR = 0-LT; 
            stepFlag = 3;              
            previousStepMillis = currentMillis;
        }
  
        else if (stepFlag == 3 && currentMillis - previousStepMillis > timerScale) {
            legLength1 = longLeg1;
            legLength2 = longLeg2;
            fr_RFB = RFBFiltered;
            fl_RFB = 0-RFBFiltered;
            bl_RFB = RFBFiltered;
            br_RFB = 0-RFBFiltered;
            fr_RLR = (footOffset +RLRFiltered) - LT;
            fl_RLR = (-footOffset -RLRFiltered) + LT;
            bl_RLR = (-footOffset +RLRFiltered) + LT;
            br_RLR = (footOffset -RLRFiltered) - LT;
            //fr_RLR = 0-LT;
            //fl_RLR = LT;
            //bl_RLR = LT;
            //br_RLR = 0-LT; 
            stepFlag = 0;              
            previousStepMillis = currentMillis;
        }
  
         
        float stepLength;
        float stepWidth;
        float stepAngle;
        float stepHyp;
  
        // timer calcs
  
        stepLength = abs(fr_RFB);
        stepWidth = abs(fr_RLR);
  
        if (stepLength == 0.0) {
          stepLength = 0.01;   // avoid divide by zero
        }
  
        stepAngle = atan(stepLength/stepWidth);  // radians       // work out actual distance of step
        stepHyp = abs(stepLength/sin(stepAngle));    // mm
  
        timerScale =  timer1 + (stepHyp/3.5);         
        
      }
    if(gyro){

      kinematics (1, fr_RFB, fr_RLR, legLength1, Roll + -1*angle(KalmanAngleRoll), Pitch + angle(KalmanAnglePitch), 0, 1, (timerScale*0.8));   // front right
      kinematics (2, fl_RFB, fl_RLR, legLength2, Roll + -1*angle(KalmanAngleRoll), Pitch + angle(KalmanAnglePitch), 0, 1, (timerScale*0.8));   // front left
      kinematics (3, bl_RFB, bl_RLR, legLength1, Roll + -1*angle(KalmanAngleRoll), Pitch + angle(KalmanAnglePitch), 0, 1, (timerScale*0.8));   // back left
      kinematics (4, br_RFB, br_RLR, legLength2, Roll + -1*angle(KalmanAngleRoll), Pitch + angle(KalmanAnglePitch), 0, 1, (timerScale*0.8));   // back right 
    }
    else{
      
      kinematics (1, fr_RFB, fr_RLR, legLength1, 0, 0, 0, 1, (timerScale*0.8));   // front right
      kinematics (2, fl_RFB, fl_RLR, legLength2, 0, 0, 0, 1, (timerScale*0.8));   // front left
      kinematics (3, bl_RFB, bl_RLR, legLength1, 0, 0, 0, 1, (timerScale*0.8));   // back left
      kinematics (4, br_RFB, br_RLR, legLength2, 0, 0, 0, 1, (timerScale*0.8));   // back right    
    }
}
int pushUpPos = maxLegHeight;

void pushUps(int pushButton){
  int upperBound = maxLegHeight;
  int lowerBound = minLegHeight;
  if (!pushButton) {
    pushUpPos += 5; // go up
  } else {
    pushUpPos -= 5; // go down
  }
  pushUpPos = constrain(pushUpPos, lowerBound, upperBound);
  kinematics (1, 0, 0, pushUpPos, 0, 0, 0, 0, 0);   // front right
  kinematics (2, 0, 0, pushUpPos, 0, 0, 0, 0, 0);   // front left
  kinematics (3, 0, 0, pushUpPos, 0, 0, 0, 0, 0);   // back left
  kinematics (4, 0, 0, pushUpPos, 0, 0, 0, 0, 0);   // back right    
}

float front_legs_z;
float back_legs_z;

void look_up_or_down(float left_trigger_val, float right_trigger_val){
  int upperBound = maxLegHeight;
  int lowerBound = minLegHeight;
  float alpha = 0.1;


   front_legs_z = ema(front_legs_z, map(left_trigger_val, 0, 1, upperBound, lowerBound), alpha);
   back_legs_z = ema(back_legs_z, map(right_trigger_val, 0, 1, upperBound, lowerBound), alpha);

      kinematics (1, 0, 0, front_legs_z, 0, 0, 0, 0, 0);   // front right
      kinematics (2, 0, 0, front_legs_z, 0, 0, 0, 0, 0);   // front left
      kinematics (3, 0, 0, back_legs_z, 0, 0, 0, 0, 0);   // back left
      kinematics (4, 0, 0, back_legs_z, 0, 0, 0, 0, 0);   // back right  
}

float angle(float gyro_val){
  float a = gyro_val;
  int bound = 20;
  if(a > bound){
    a = bound;
    }
  if(a < -bound){
    a = -bound;
    }
  return a;
}//use: kinematics (1, fr_RFB, fr_RLR, legLength1, -1*angle(LegRollFiltered), angle(LegPitchFiltered), 0, 1, (timerScale*0.8));   // front right

void Roll_Pitch(float R, float P){
    Roll = angle(map(R, -1, 1, 20, -20));
    Pitch = angle(map(P, -1, 1, 20, -20));
}
float left_legs_x;
float left_legs_y;
float left_legs_z = maxLegHeight;
float right_legs_x;
float right_legs_y;
float right_legs_z = maxLegHeight;
float alpha = 0.1;

  // Exponential Moving Average (EMA) helper function
float ema(float current, float target, float alpha) {
  return current * (1.0 - alpha) + target * alpha;
}

void LRControl(float left_stick_horizontal, float left_stick_vertical, float left_trigger, float right_stick_horizontal, float right_stick_vertical, float right_trigger) {
  int upperBound = maxLegHeight;
  int lowerBound = minLegHeight;

  left_legs_x = ema(left_legs_x, -map(left_stick_vertical, -1, 1, -300, 300), alpha);
  left_legs_y = ema(left_legs_y, -map(left_stick_horizontal, -1, 1, -100, 100), alpha);
  left_legs_z = ema(left_legs_z, map(left_trigger, 0, 1, upperBound, lowerBound), alpha);

  right_legs_x = ema(right_legs_x, -map(right_stick_vertical, -1, 1, -300, 300), alpha);
  right_legs_y = ema(right_legs_y, map(right_stick_horizontal, -1, 1, -100, 100), alpha);
  right_legs_z = ema(right_legs_z, map(right_trigger, 0, 1, upperBound, lowerBound), alpha);

  kinematics(2, left_legs_x, left_legs_y, left_legs_z, 0, 0, 0, 0, 0);
  kinematics(1, right_legs_x, right_legs_y, right_legs_z, 0, 0, 0, 0, 0);
  kinematics(4, right_legs_x, right_legs_y, right_legs_z, 0, 0, 0, 0, 0);
  kinematics(3, left_legs_x, left_legs_y, left_legs_z, 0, 0, 0, 0, 0);
}
