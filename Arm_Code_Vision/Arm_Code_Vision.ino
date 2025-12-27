#include <AccelStepper.h>

#define STEPS_PER_REV 2048

AccelStepper motorL(AccelStepper::FULL4WIRE, 8, 10, 9, 11);
AccelStepper motorR(AccelStepper::FULL4WIRE, 2, 5, 3, 6);

int motorSpeed = 600;
int motorAccel = 600;

int stepsRight = 4000;
int stepsLeft = -4000;

String objName = "";
int side = 0;
int distance = 0;
int radius = 0;

bool commandReady = false;

void setup() {
  Serial.begin(9600);

  motorL.setMaxSpeed(motorSpeed);
  motorL.setAcceleration(motorAccel);

  motorR.setMaxSpeed(motorSpeed);
  motorR.setAcceleration(motorAccel);

  motorL.setCurrentPosition(0);
  motorR.setCurrentPosition(0);

  Serial.println("=== SpiRob Control Initialized ===");
  Serial.println("Send command in format: name,side,distance,radius");
  Serial.println("Example: ball,1,3000,500");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    int firstComma = input.indexOf(',');
    int secondComma = input.indexOf(',', firstComma + 1);
    int thirdComma = input.indexOf(',', secondComma + 1);

    objName = input.substring(0, firstComma);
    side = input.substring(firstComma + 1, secondComma).toInt();
    distance = input.substring(secondComma + 1, thirdComma).toInt();
    radius = input.substring(thirdComma + 1).toInt();

    commandReady = true;

    Serial.print("Object: "); Serial.println(objName);
    Serial.print("Side: "); Serial.println(side);
    Serial.print("Distance: "); Serial.println(distance);
    Serial.print("Radius: "); Serial.println(radius);
  }

  if (commandReady) {
    if (side == 1) {
      motorL.run();
      motorR.run();

      if (done) return;

      switch (stepState) {

        case 0:
          delay(2000);
          motorL.moveTo(stepsLeft);
          motorR.moveTo(stepsLeft);
          stepState = 1;
          break;

        case 1:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            motorL.setMaxSpeed(400);
            motorL.setAcceleration(100);
            motorR.setMaxSpeed(700);
            motorR.setAcceleration(300);
            motorL.moveTo(-1000);
            motorR.moveTo(750);
            stepState = 2;
          }
          break;

        case 2:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            motorL.setMaxSpeed(700);
            motorL.setAcceleration(300);
            motorR.setMaxSpeed(500);
            motorR.setAcceleration(200);
            motorL.moveTo(500);
            motorR.moveTo(1750);
            stepState = 3;
          }
          break;

        case 3:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            motorL.setMaxSpeed(400);
            motorL.setAcceleration(100);
            motorR.setMaxSpeed(700);
            motorR.setAcceleration(300);
            motorL.moveTo(1500);
            motorR.moveTo(4000);
            stepState = 4;
          }
          break;

        case 4:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            done = true;
          }
          break;
      }
    }

    else if (side == -1) {
      motorL.run();
      motorR.run();

      if (done) return;

      switch (stepState) {

        case 0:
          delay(2000);
          motorL.moveTo(stepsRight);
          motorR.moveTo(stepsRight);
          stepState = 1;
          break;

        case 1:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            motorR.setMaxSpeed(400);
            motorR.setAcceleration(100);
            motorL.setMaxSpeed(700);
            motorL.setAcceleration(300);
            motorR.moveTo(1000);
            motorL.moveTo(-750);
            stepState = 2;
          }
          break;

        case 2:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            motorR.setMaxSpeed(700);
            motorR.setAcceleration(300);
            motorL.setMaxSpeed(500);
            motorL.setAcceleration(200);
            motorR.moveTo(-500);
            motorL.moveTo(-1750);
            stepState = 3;
          }
          break;

        case 3:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            motorR.setMaxSpeed(400);
            motorR.setAcceleration(100);
            motorL.setMaxSpeed(700);
            motorL.setAcceleration(300);
            motorR.moveTo(-1500);
            motorL.moveTo(-4000);
            stepState = 4;
          }
          break;

        case 4:
          if (motorL.distanceToGo() == 0 && motorR.distanceToGo() == 0) {
            done = true;
          }
          break;
      }
    }
    Serial.println("Object grabbed successfully!");
    commandReady = false;
  }
}