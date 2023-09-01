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
int PER;  //PERIODE

//Variables globales
int inByte = 0;

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

void loop() {
  
  if (BT1.available()>0 || Serial.available()>0)
  {
    if (BT1.available()>0)
    {
      inByte = BT1.read();
    }
    else if (Serial.available()>0)
    {
      inByte = Serial.read();
    }
    if (inByte=='0') //OFF
    {
      digitalWrite(SLP_PIN_AR,LOW);
      digitalWrite(SLP_PIN_DEC,LOW);
    }
    else if (inByte=='1') //AR - x1 ON
    {
      digitalWrite(SLP_PIN_AR,HIGH);
      digitalWrite(DIR_PIN_AR,LOW);
      STP = STP_PIN_AR;
      PER = PER_X1;
    }
    else if (inByte=='2') //AR - x17
    {
      digitalWrite(SLP_PIN_AR,HIGH);
      digitalWrite(DIR_PIN_AR,LOW);
      STP = STP_PIN_AR;
      PER = PER_X17;
    }
    else if (inByte=='3') //AR + x17
    {
      digitalWrite(SLP_PIN_AR,HIGH);
      digitalWrite(DIR_PIN_AR,HIGH);
      STP = STP_PIN_AR;
      PER = PER_X17;
    }
    else if (inByte=='4') //AR - x5
    {
      digitalWrite(SLP_PIN_AR,HIGH);
      digitalWrite(DIR_PIN_AR,LOW);
      STP = STP_PIN_AR;
      PER = PER_X5;
    }
    else if (inByte=='5') //AR + x5
    {
      digitalWrite(SLP_PIN_AR,HIGH);
      digitalWrite(DIR_PIN_AR,HIGH);
      STP = STP_PIN_AR;
      PER = PER_X5;
    }
    else if (inByte=='6') //DEC + x17
    {
      digitalWrite(SLP_PIN_DEC,HIGH);
      digitalWrite(DIR_PIN_DEC,LOW);
      STP = STP_PIN_DEC;
      PER = PER_X17;
    }
    else if (inByte=='7') //DEC - x17
    {
      digitalWrite(SLP_PIN_DEC,HIGH);
      digitalWrite(DIR_PIN_DEC,HIGH);
      STP = STP_PIN_DEC;
      PER = PER_X17;
    }
    else if (inByte=='8') //DEC + x5
    {
      digitalWrite(SLP_PIN_DEC,HIGH);
      digitalWrite(DIR_PIN_DEC,LOW);
      STP = STP_PIN_DEC;
      PER = PER_X5;
    }
    else if (inByte=='9') //DEC - x5
    {
      digitalWrite(SLP_PIN_DEC,HIGH);
      digitalWrite(DIR_PIN_DEC,HIGH);
      STP = STP_PIN_DEC;
      PER = PER_X5;
    }
  }
  // put your main code here, to run repeatedly:
  digitalWrite(STP,HIGH);
  delay(PER);
  digitalWrite(STP,LOW);
  delay(PER);
  digitalWrite(STP,HIGH);
  delay(PER);
  digitalWrite(STP,LOW);
  delay(PER);
  digitalWrite(STP,HIGH);
  delay(PER);
  digitalWrite(STP,LOW);
  delay(PER);
  digitalWrite(STP,HIGH);
  delay(PER);
  digitalWrite(STP,LOW);
  delay(PER);

}
