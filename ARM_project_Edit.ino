#include <AccelStepper.h>

#define STEPS_PER_REV 2048

AccelStepper motorL(AccelStepper::FULL4WIRE, 8, 10, 9, 11);
AccelStepper motorR(AccelStepper::FULL4WIRE, 2, 5, 3, 6);

int motorSpeed = 600;  
int motorAccel = 400;  

int stepsRight = 3200;   
int stepsLeft  = -4000;
int stepsNeutral = 0;

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
    Serial.println("🟢 الذراع ينحني لليمين");
    motorL.moveTo(stepsRight);
    motorR.moveTo(stepsRight);
    while (motorL.distanceToGo() != 0 || motorR.distanceToGo() != 0) {
      motorL.run();
      motorR.run();
    }
    delay(2000);

    Serial.println("🔵 الذراع ينحني لليسار");
    motorL.moveTo(stepsLeft);
    motorR.moveTo(stepsLeft);
    while (motorL.distanceToGo() != 0 || motorR.distanceToGo() != 0) {
      motorL.run();
      motorR.run();
    }
    delay(2000);

    Serial.println("⚪ العودة إلى المنتصف");
    motorL.moveTo(stepsNeutral);
    motorR.moveTo(stepsNeutral);
    while (motorL.distanceToGo() != 0 || motorR.distanceToGo() != 0) {
      motorL.run();
      motorR.run();
    }

    Serial.println("✅ انتهى التنفيذ لمرة واحدة فقط");
    done = true;
  }
}