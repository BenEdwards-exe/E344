// B.J. Edwards
// 22738002
// October 2021

#include "Keyboard.h"


const int ovPin = 10; // Overcharge Pin
const int batteryVoltagePin = 0; // Battery Voltage Pin
const int supplyVoltagePin = 1; // Supply Voltage Pin
const int batteryCurrentPin = 2; // Battery Current Pin
const int ambientLightPin = 9; // Ambient Light Pin

int overchargeStatus = 0;

int battSensorVal = 0;
float battVoltage = 0;
float sensorVoltage = 0;

int supplSensorVal = 0;
float supplVoltage = 0;
float supplSensorVoltage = 0;

int currentSensorVal = 0;
float currentSensorVoltage = 0;
float batteryCurrent = 0;

int ambientSensorVal = 0;
float ambientSensorVoltage = 0;
int ambientLightPercentage = 0;


unsigned long printTimer = millis();

void setup() {
  // Turn on built in LED to signal setup start
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  /// Serial Setup ///
  // open the serial port:
  Serial.begin(9600);
  // initialize control over the keyboard:
  Keyboard.begin();

  // initialize the overcharge pin
  pinMode(ovPin, OUTPUT);


  // Turn off built in LED to signal setup end
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {

  checkCharging();

  // Read analogue inputs
  readBatteryVoltage();
  readSupplyVoltage();
  readBatteryCurrent();
  readAmbientLightLevel();

  if (millis() - printTimer >= 1000.0) {
    displayOutput();
    printTimer = millis();
  }

}


// Format the string for output reading
void displayOutput()
{
  String out = String( String(overchargeStatus, 2) + ","
                       + String(battVoltage, 2) + ","
                       + String(supplVoltage, 2) + ","
                       + String(batteryCurrent, 2) + ","
                       + String(ambientLightPercentage) + "\n");

  Serial.print(out);

}

// Read the ambient light level as a percentage
void readAmbientLightLevel()
{
  // read the analogue input
  ambientSensorVal = analogRead(ambientLightPin);
  // convert analogue reading to a voltage
  ambientSensorVoltage = ambientSensorVal * (5.0 / 1023.0);
  // convert voltage reading to a percentage
  ambientLightPercentage = (int) constrain((1.0 - ambientSensorVoltage / (4.56 - 0.01)) * 100, 0, 100);
}



// Read the battery current
void readBatteryCurrent()
{
  // read the analogue input
  currentSensorVal = analogRead(batteryCurrentPin);
  // convert analogue reading to a voltage
  currentSensorVoltage = currentSensorVal * (5.0 / 1023.0);
  // convert voltage reading to current flow
  batteryCurrent = (currentSensorVoltage - 1.75) * 0.2;
}

// Read the supply voltage
void readSupplyVoltage()
{
  // read the analogue input
  supplSensorVal = analogRead(supplyVoltagePin);
  // convert analogue reading to a voltage
  supplSensorVoltage = supplSensorVal * (5.0 / 1023.0);
  supplVoltage = supplSensorVoltage * (500.0 / 93.0);
}

// Read battery voltage
void readBatteryVoltage()
{
  // read the analogue input
  battSensorVal = analogRead(batteryVoltagePin);
  // convert analog reading to a voltage
  sensorVoltage = battSensorVal * (5.0 / 1023.0);
  battVoltage = sensorVoltage * (9.0 / 23.0) + 5.54826;
}

// Check for user input to set overcharge control signal
void checkCharging()
{
  // check for incoming serial data:
  if (Serial.available() > 0) {
    // read incoming serial data:
    String userIn = Serial.readString();
    userIn.trim();
    if (userIn.equals("OV1")) {
      digitalWrite(ovPin, HIGH);
      overchargeStatus = 1;
    }
    else if (userIn.equals("OV0")) {
      digitalWrite(ovPin, LOW);
      overchargeStatus = 0;
    }
  }
}
