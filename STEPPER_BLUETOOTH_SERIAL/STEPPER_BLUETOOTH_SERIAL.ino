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
long ar_steps = 0;
int ar_dir = 0;
int ar_per = 52;
long dec_steps = 0;
int dec_dir = 0;
int dec_per = 0;
int stop = 0;
int period = 0;

// Variables to store the last time the LEDs were updated
unsigned long t0_ar  = 0;
unsigned long t0_dec = 0;

// Define counters
int n_ar = 0;
int n_de = 0;
long step_ar = 0;
long step_de = 0;

// Define checkers
int de_ready = 0;
int ar_ready = 0;

void setup() {
  //Inicio módulo Bluetooth
  BT1.begin(19200);
  Serial.begin(19200);
  
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

  // Turn on AR and DEC motors
  digitalWrite(SLP_PIN_AR, HIGH);
  digitalWrite(SLP_PIN_DEC, HIGH);

}

void loop() {
  if (BT1.available()>7 || Serial.available()>7) {
    stop = Serial.parseInt();
    ar_steps = Serial.parseInt();
    ar_dir = Serial.parseInt();
    ar_per = Serial.parseInt();
    dec_steps = Serial.parseInt();
    dec_dir = Serial.parseInt();
    dec_per = Serial.parseInt();
    Serial.println(ar_steps);
    Serial.println(dec_steps);

    // Set the pins on
    digitalWrite(DIR_PIN_AR, ar_dir);
    digitalWrite(DIR_PIN_DEC, dec_dir);
    
    // Set counter to zero
    n_ar = 0;
    n_de = 0;
    step_ar = 0;
    step_de = 0;

    // Set checkers to 0
    if (ar_steps>0) {
      ar_ready = 0;
    }
    else {
      ar_ready = 1;
    }
    if (dec_steps > 0) {
      de_ready = 0;
    }
    else {
      de_ready = 1;
    }
  }

  // Check if stop
  if (stop == 1) {
    return;
  }

  // Get the current time
  unsigned long t1 = millis();
  
  // Check if it's time to blink the AR
  if (t1 - t0_ar >= ar_per && ar_per > 0) {
    // Save the current time
    t0_ar = t1;

    // Toggle the AR pin
    digitalWrite(STP_PIN_AR, !digitalRead(STP_PIN_AR));
    
    // Count the switch
    n_ar = n_ar + 1;

    // Add step
    if (n_ar==2) {
      n_ar = 0;
      step_ar = step_ar + 1;
    }

    // Check if final step
    if (step_ar>=ar_steps && ar_steps>0) {
      step_ar = 0;
      ar_steps = 0;
      ar_per = 52;
      ar_dir = 0;
      digitalWrite(DIR_PIN_AR, ar_dir);
      ar_ready = 1;
      if (ar_ready + de_ready == 2) {
        Serial.println("Ready!");
      }
    }
  }

  // Check if it's time to blink the DEC
  if (t1 - t0_dec >= dec_per && dec_per > 0) {
    // Save the current time
    t0_dec = t1;

    // Toggle the AR pin
    digitalWrite(STP_PIN_DEC, !digitalRead(STP_PIN_DEC));
    
    // Count the switch
    n_de = n_de + 1;

    // Add step
    if (n_de==2) {
      n_de = 0;
      step_de = step_de + 1;
    }

    // Check if final step
    if (step_de>=dec_steps && dec_steps > 0) {
      step_de = 0;
      dec_steps = 0;
      dec_per = 0;
      dec_dir = 0;
      digitalWrite(DIR_PIN_DEC, dec_dir);
      de_ready = 1;
      if (ar_ready + de_ready == 2) {
        Serial.println("Ready!");
      }
    }
  }
}
