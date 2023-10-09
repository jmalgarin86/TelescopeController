#include <SoftwareSerial.h>
SoftwareSerial BT1(7,13); // RX, TX

//Versión V3.0. Mueve simultaneamente los motores de AR y DEC

//Pines Stepper AR
#define DIR_PIN_AR 2
#define STP_PIN_AR 3
#define MS1_PIN_AR 4
#define MS2_PIN_AR 5
#define SLP_PIN_AR 6

//Pines Stepper DEC
#define DIR_PIN_DEC 8
#define STP_PIN_DEC 9
#define MS1_PIN_DEC 10
#define MS2_PIN_DEC 11
#define SLP_PIN_DEC 12

//Variables globales
int ar_steps = 0;
int ar_dir = 1;
int ar_per = 0;
int dec_steps = 0;
int dec_dir = 1;
int dec_per = 0;
int stop = 0;
int period = 0;

void setup() {
  //Inicio módulo Bluetooth
  BT1.begin(115200);
  Serial.begin(115200);
  
  //Modos de pines Stepper A
  pinMode(DIR_PIN_AR,OUTPUT);
  pinMode(STP_PIN_AR,OUTPUT);
  pinMode(MS1_PIN_AR,OUTPUT);
  pinMode(MS2_PIN_AR,OUTPUT);
  pinMode(SLP_PIN_AR,OUTPUT);

  //Modos de pines Stepper B
  pinMode(DIR_PIN_DEC,OUTPUT);
  pinMode(STP_PIN_DEC,OUTPUT);
  pinMode(MS1_PIN_DEC,OUTPUT);
  pinMode(MS2_PIN_DEC,OUTPUT);
  pinMode(SLP_PIN_DEC,OUTPUT);

  //Configuración Stepper A
  digitalWrite(SLP_PIN_AR,HIGH);
  digitalWrite(MS1_PIN_AR,LOW);
  digitalWrite(MS2_PIN_AR,LOW);

  //Configuración Stepper B
  digitalWrite(SLP_PIN_DEC,HIGH);
  digitalWrite(MS1_PIN_DEC,LOW);
  digitalWrite(MS2_PIN_DEC,LOW);

}

void moveSteppers() {
  // Empty serial buffer
  while (Serial.available() > 0) {
    char _ = Serial.read(); // Read and discard the character
  }
  
  int n_ar = 0;
  int n_de = 0;
  int step_ar = 0;
  int step_de = 0;
  int next_ar = 1;
  int next_de = 1;

  // Avoid axis if perio is zero
  if (ar_per==0) {
    next_ar = 0;
  }
  if (dec_per==0) {
    next_de = 0;
  }

  // Set pins
  digitalWrite(DIR_PIN_AR, ar_dir);
  digitalWrite(DIR_PIN_DEC, dec_dir);
  digitalWrite(SLP_PIN_AR, HIGH);
  digitalWrite(SLP_PIN_DEC, HIGH);

  // Variables to store the last time the LEDs were updated
  unsigned long t0_ar  = 0;
  unsigned long t0_dec = 0;
  // New step while no new serial available
  while (BT1.available()==0 && Serial.available()==0 && (next_ar+next_de>0)){
    // Get the current time
    unsigned long t1 = millis();
    
    // Check if it's time to blink the AR
    if (t1 - t0_ar >= ar_per && next_ar == 1) {
      // Save the current time
      t0_ar = t1;

      // Toggle the AR pin
      if (stop==2) {
        digitalWrite(STP_PIN_AR, LOW);
      }
      else {
        digitalWrite(STP_PIN_AR, !digitalRead(STP_PIN_AR));
      }
      
      // Count the switch
      n_ar = n_ar + 1;

      // Add step
      if (n_ar==2) {
        n_ar = 0;
        step_ar = step_ar + 1;
      }

      // Check if final step
      if (ar_steps==0) {
        next_ar = 1;
      }
      else if (step_ar>=ar_steps) {
        next_ar = 0;
        if (stop==1) {
          next_de = 0;
        }
      }
    }

    // Check if it's time to blink the DEC
    if (t1 - t0_dec >= dec_per && next_de == 1) {
      // Save the current time
      t0_dec = t1;

      // Togle the DEC pin
      digitalWrite(STP_PIN_DEC, !digitalRead(STP_PIN_DEC));

      // Count the switch
      n_de = n_de + 1;

      // Add step
      if (n_de==2) {
        n_de = 0;
        step_de = step_de + 1;
      }

      // Check if final step
      if (dec_steps==0) {
        next_de = 1;
      }
      else if (step_de>=dec_steps) {
        next_de = 0;
        if (stop==1) {
          next_ar = 0;
        }
      }
    }
  }

  digitalWrite(SLP_PIN_AR, LOW);
  digitalWrite(SLP_PIN_DEC, LOW);

  if (next_ar+next_de==0) {
    Serial.println("Ready!");
  }

}

void loop() {
  // stop = 1 is used to finish AR axis once DEC axis is ready
  // stop = 2 is used to do not blank the signal that do the steps, so the moveSteppers just wait until the number of steps is done
  if (BT1.available()>7 || Serial.available()>7) {
    stop = Serial.parseInt();
    ar_steps = Serial.parseInt();
    ar_dir = Serial.parseInt();
    ar_per = Serial.parseInt();
    dec_steps = Serial.parseInt();
    dec_dir = Serial.parseInt();
    dec_per = Serial.parseInt();
    moveSteppers();
  }
}

