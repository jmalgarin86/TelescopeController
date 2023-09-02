#include <SoftwareSerial.h>
SoftwareSerial BT1(7,13); // RX, TX

//Versión V2.1 Corrige la dirección del eje de AR

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

int STP;  //STEP
int PER_X1 = 52;  //PERIODE x1
int PER_X5 = 10; //PERIODE x10
int PER_X17 = 3;  //PERIODE x17
int PER = PER_X17;  //PERIODE

//Variables globales
int ar_steps = 0;
int ar_dir = 1;
int dec_steps = 0;
int dec_dir = 1;
int follow = 0;
int period = 0;

void setup() {
  //Inicio módulo Bluetooth
  BT1.begin(9600);
  Serial.begin(9600);
  
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

void followStepper(int DIR_PIN, int SLP_PIN, int STP_PIN, int dir){
  // empty serial buffer
  while (Serial.available() > 0) {
    char _ = Serial.read(); // Read and discard the character
  }

  // set pins
  digitalWrite(DIR_PIN, dir);
  digitalWrite(SLP_PIN, HIGH);
  
  // Follow while no new serial available
  while (BT1.available()==0 && Serial.available()==0){
    for (int i = 0; i<4; i++){
      digitalWrite(STP_PIN, HIGH);
      delay(period);
      digitalWrite(STP_PIN, LOW);
      delay(period);
    }
  }
  digitalWrite(SLP_PIN, LOW);
}

void moveSteppers(){
  digitalWrite(DIR_PIN_AR, ar_dir);
  digitalWrite(DIR_PIN_DEC, dec_dir);
  digitalWrite(SLP_PIN_AR, HIGH);
  digitalWrite(SLP_PIN_DEC, HIGH);
  if(ar_steps<=dec_steps){
    for (int i = 0; i<4*(dec_steps-ar_steps); i++){
      digitalWrite(STP_PIN_DEC, HIGH);
      delay(period);
      digitalWrite(STP_PIN_DEC, LOW);
      delay(period);
    }
    for (int i = 0; i<4*ar_steps; i++){
      digitalWrite(STP_PIN_AR, HIGH);
      digitalWrite(STP_PIN_DEC, HIGH);
      delay(period);
      digitalWrite(STP_PIN_AR, LOW);
      digitalWrite(STP_PIN_DEC, LOW);
      delay(period);
    }
  }
  else{
    for (int i = 0; i<4*(ar_steps-dec_steps); i++){
      digitalWrite(STP_PIN_AR, HIGH);
      delay(period);
      digitalWrite(STP_PIN_AR, LOW);
      delay(period);
    }
    for (int i = 0; i<4*dec_steps; i++){
      digitalWrite(STP_PIN_AR, HIGH);
      digitalWrite(STP_PIN_DEC, HIGH);
      delay(period);
      digitalWrite(STP_PIN_AR, LOW);
      digitalWrite(STP_PIN_DEC, LOW);
      delay(period);
    }
  }
  digitalWrite(SLP_PIN_AR, LOW);
  digitalWrite(SLP_PIN_DEC, LOW);
  if (follow==1){
    period = 52;
    ar_dir = 1;
    followStepper(DIR_PIN_AR, SLP_PIN_AR, STP_PIN_AR, ar_dir);
  }
  else if (follow==2){
    followStepper(DIR_PIN_AR, SLP_PIN_AR, STP_PIN_AR, ar_dir);
  }
  else if (follow==3){
    followStepper(DIR_PIN_DEC, SLP_PIN_DEC, STP_PIN_DEC, dec_dir);
  }
}


void loop() {
  if (BT1.available()>6 || Serial.available()>6)
  {
    if (BT1.available()>6)
    {
      follow = Serial.parseInt();
      ar_steps = Serial.parseInt();
      ar_dir = Serial.parseInt();
      dec_steps = Serial.parseInt();
      dec_dir = Serial.parseInt();
      period = Serial.parseInt();
    }
    else if (Serial.available()>6)
    {
      follow = Serial.parseInt();
      ar_steps = Serial.parseInt();
      ar_dir = Serial.parseInt();
      dec_steps = Serial.parseInt();
      dec_dir = Serial.parseInt();
      period = Serial.parseInt();
    }
    moveSteppers();
  }
}
