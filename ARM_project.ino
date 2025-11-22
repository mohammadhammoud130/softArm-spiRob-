#include <Stepper.h>
#define STEPS_PER_REV 2048

Stepper motorL(STEPS_PER_REV, 8, 10, 9, 11);
Stepper motorR(STEPS_PER_REV, 2, 5, 3, 6);

const float D_in_S = 0.0521;
const float R = 5.0;
const float C = 0.5;

int SpeedOFMotor = 20;

long currentSteps = 0;
bool done = false;

unsigned long previousMillis = 0;
const unsigned long interval = 2000;
int state = 0;

// زوايا الانحناء
float angleRight = 7.0;
float angleLeft = -11.0;
float angleNeutral = 0.0;

int stepsFromAngle(float O) {
  float L = R * (exp(C * abs(O)) - 1);
  int steps = L / D_in_S;
  return steps;
}

void moveBothMotors(float O_target) {
  int targetSteps = stepsFromAngle(O_target);
  int stepsToMove = targetSteps - currentSteps;
  int dir = (stepsToMove > 0) ? 1 : -1;
  int steps = abs(stepsToMove);

  for (int i = 0; i < steps; i++) {
    motorL.step(dir);
    motorR.step(dir);
  }

  currentSteps = targetSteps;

  Serial.print("Moved to angle: ");
  Serial.print(O_target);
  Serial.print(" | Steps: ");
  Serial.println(currentSteps);
}

void setup() {
  motorL.setSpeed(SpeedOFMotor);
  motorR.setSpeed(SpeedOFMotor);
  Serial.begin(9600);
}

void loop() {
  unsigned long currentMillis = millis();

  if (!done) {



    Serial.println("🟢 الذراع ينحني لليمين");
    moveBothMotors(angleRight);


    Serial.println("🔵 الذراع ينحني لليسار");
    moveBothMotors(angleLeft);


    Serial.println("⚪ العودة إلى المنتصف");
    moveBothMotors(angleNeutral);

    done = true;
  }
}