#ifndef CONFIG_H
#define CONFIG_H

float offSet10 = -0.489;      //ODrive 1, axis 0     // hips - right front / Positive increment = up
float offSet11 = 0.496;      //ODrive 1, axis 1     // hips - right back // Positive increment = up
float offSet40 = 0.47;      //ODrive 4, axis 0     // hips - left front // Positive increment = down
float offSet41 = 0.11;      //ODrive 4, axis 1     // hips - left back. // Positive increment = down

float offSet21 = -0.2;      //ODrive 2, axis 1     // shoulder - right front // Positive Increment = shoulder forward
float offSet31 = 0.95;       //ODrive 3, axis 1     // shoulder - right rear // Positive increment = shoulder forward
float offSet51 = 0.7;       //ODrive 5, axis 0     // shoulder - left front // Positive Increment = shoulder back
float offSet61 =  -0.8;     //ODrive 6, axis 1     // shoulder - left rear // Positive increment = shoulder back

float offSet20 = -1.3;      //ODrive 2, axis 0     // knee - right front // Positive Increment = knee backward
float offSet30 = 0.5;       //ODrive 3, axis 0     // knee - right rear // Positive Increment = knee forward
float offSet50 = 0.9;      //ODrive 5, axis 0     // knee - left front // Neg increment = knee backward
float offSet60 = -0.7;      //ODrive 6, axis 0     // knee - left rear // Positive Increment = knee forward



#endif