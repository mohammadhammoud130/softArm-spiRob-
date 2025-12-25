#include <AccelStepper.h>

#define STEPS_PER_REV 2048

AccelStepper motorL(AccelStepper::FULL4WIRE, 8, 10, 9, 11);
AccelStepper motorR(AccelStepper::FULL4WIRE, 2, 5, 3, 6);

int motorSpeed = 600;  
int motorAccel = 600;  

int stepsRight = 4000;   
int stepsLeft  = -4000;
int stepsNeutral = 0;

int steps500 = 1000;
int steps5000 = 10000;

bool done = false;

void setup() {
  Serial.begin(9600);

  motorL.setMaxSpeed(motorSpeed);
  motorL.setAcceleration(motorAccel);

  motorR.setMaxSpeed(motorSpeed);
  motorR.setAcceleration(motorAccel);

  motorL.setCurrentPosition(0);
  motorR.setCurrentPosition(0);

  Serial.println("=== SpiRob Control Initialized ===");
}

void loop() {
  if (!done) {
    
    delay(2000);

    motorL.moveTo(stepsLeft);
    motorR.moveTo(stepsLeft);
    while (motorL.distanceToGo() != 0 || motorR.distanceToGo() != 0) {
      motorL.run();
      motorR.run();
    }
   
    delay(500);

    
    motorL.setMaxSpeed(400);
    motorL.setAcceleration(100);
    motorR.setMaxSpeed(700); 
    motorR.setAcceleration(300);
    motorL.moveTo(steps500);
    motorR.moveTo(steps5000);
    while (motorL.distanceToGo() != 0 || motorR.distanceToGo() != 0) {
      motorL.run();
      motorR.run();
    }

    done = true;
  }
}