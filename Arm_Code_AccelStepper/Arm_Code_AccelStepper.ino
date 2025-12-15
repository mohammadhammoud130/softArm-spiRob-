#include <AccelStepper.h>

#define STEPS_PER_REV 2048

// تعريف الموتورات (نوع DRIVER = 4 أسلاك ULN2003)
AccelStepper motorL(AccelStepper::FULL4WIRE, 8, 10, 9, 11);
AccelStepper motorR(AccelStepper::FULL4WIRE, 2, 5, 3, 6);

int motorSpeed = 1000;   // السرعة القصوى
int motorAccel = 600;    // التسارع

// زوايا الانحناء (نحو اليمين واليسار والمنتصف)
int stepsRight = 2000;   // يمين
int stepsLeft  = -3000;  // يسار
int stepsNeutral = 0;    // المنتصف

bool done = false;

void setup() {
  Serial.begin(9600);

  motorL.setMaxSpeed(motorSpeed);
  motorL.setAcceleration(motorAccel);

  motorR.setMaxSpeed(motorSpeed);
  motorR.setAcceleration(motorAccel);

  // ✅ تصفير الخطوات قبل البدء
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