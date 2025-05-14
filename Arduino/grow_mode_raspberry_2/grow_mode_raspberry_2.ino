
///*******************************************************************


#include <DS3231_Simple.h>
DS3231_Simple Clock;


const int Grow = 0;//grow mode day time
const int Night = 1;//night mode 
int LedNo = 10;
int ModePin = Grow;
int FadePin = 10;
int Fade2Pin = 9;
int fadeValue = 0;
int fade2Value = 220;
int Relay1Pin = 13;
int Relay2Pin = 12;
int LightOnPin = 7;//LIGHT ON / OFF pin High= ON from Raspberry Pi
int GrowNightPin = 8;
bool Manual;
bool ManMode;
int LightOn ;//read input command from raspberry

int Min;
const int high_light_intensity = 0;
const int low_light_intensity = 256;
const int night_int = 1;

int dawn_time = 0600;
int dusk_time = 2100;


//Grow lights On
void GrowMode(){ //grow light process
ModePin = Grow;
digitalWrite (Relay1Pin ,LOW); 
digitalWrite (Relay2Pin ,Grow); 
}
//Grow lights OFF small light is ON
void NightMode(){
ModePin = Night;
digitalWrite (Relay1Pin ,Night);
digitalWrite (Relay2Pin ,Night);
//digitalWrite (IR_outPin ,LOW); 
}

void setup() {

  pinMode (Relay1Pin , OUTPUT);
  pinMode (Relay2Pin , OUTPUT);
//                                                                                                                                                                                                                                                                                                                                  ``  ``````````````````  pinMode (IR_outPin , OUTPUT);
  pinMode (GrowNightPin , INPUT_PULLUP);
  pinMode (LightOnPin,INPUT_PULLUP); 
  pinMode  (FadePin,OUTPUT);
  
//FastLED.addLeds<NEOPIXEL, 6>(leds, NUM_LEDS);
  Serial.begin(9600);
  Clock.begin();
  
  Serial.println();
  Serial.println();
  //  Create a variable to hold the data 
  DateTime MyTimestamp;
  // Load it with the date and time you want to set, for example
  //   Saturday the 3rd of October 2020 at 14:17 and 33 Seconds...
  MyTimestamp.Day    = 9;
  MyTimestamp.Month  = 10;
  MyTimestamp.Year   = 24; 
  MyTimestamp.Hour   = 15;
  MyTimestamp.Minute = 48;
  MyTimestamp.Second = 30;
  
//   Then write it to the clock
//

//Clock.write(MyTimestamp);// this is the clock setup line, please activate it when you need to adjust controller real time
  
  // And use it, we will read it back for example...  
  Serial.print("The time has been set to: ");
  Clock.printTo(Serial);
  Serial.println();

}

void loop() 
{ 
 
 // if (fadeValue > 1024){ fadeValue =1024;}
 // if (fadeValue < 200){ fadeValue =200;}
 LightOn = digitalRead (LightOnPin );
 if (LightOn == LOW ){fade2Value = 0;
    analogWrite(FadePin, HIGH);//grow light fade commandlights off
    analogWrite(Fade2Pin,LOW);//grow light fade2 command lights off
 }
 else if (fadeValue <= 255) { //Anton's change
  fade2Value = 255;
  analogWrite(FadePin, fadeValue);//grow light fade command
  analogWrite(Fade2Pin, fade2Value);//grow light fade2 command
 }
 else {
  //fade2Value = 255;
  digitalWrite(FadePin, HIGH); //Anton's change
 }
  // Create a variable to hold the data 
  DateTime MyDateAndTime;

  // Ask the clock for the data.
  MyDateAndTime = Clock.read();
  int t = MyDateAndTime.Hour * 100 + MyDateAndTime.Minute; // Another way to represent time, easier to play with
  
  // And use it
 Serial.println("TIME");//הצגת כותרת TIME
 Serial.print("Hour: ");   Serial.println(MyDateAndTime.Hour);//הצגת שעה
 Serial.print("Minute: "); Serial.println(MyDateAndTime.Minute);//הצגת דקות
 Serial.print("Second: "); Serial.println(MyDateAndTime.Second);//הצגת שניות
 Serial.println("DATE");// הצגת תאריך
 Serial.print("Year: ");   Serial.println(MyDateAndTime.Year);
 Serial.print("Month: ");  Serial.println(MyDateAndTime.Month);
 Serial.print("Day: ");    Serial.println(MyDateAndTime.Day);
 Serial.println("------------------------------");
 //Serial.print("Min: ");    Serial.println(Min);
 //Serial.print("Light Sensor: ");    Serial.println(sensorValue);
 Serial.print("Light Mode: ");    Serial.println(ModePin);
Serial.print("Light ON/OFF (Raspberry): ");    Serial.println(LightOn);
 Serial.print("Fade Value: ");    Serial.println(fadeValue);
 Serial.print("Fan Pin: ");    Serial.println(LightOnPin);
  Serial.print("Fade2 Value: ");    Serial.println(fade2Value);
 
 Serial.print("Light On PIN" ); Serial.println(LightOn);
  
 //  ***  ON OFF *** 
  //Grow mode means Light ON , Night mode means Light OFF
  if (t>= dawn_time and t< dusk_time){
    GrowMode();
  }
  else{
    fadeValue = 50; // I have added this line to make sure that lights AND fans are off  Pini(03_2024)50 is max level for new PS
    NightMode();
  }

 
//**** DIMMING ****
//Active fade value is between 0 and 255 where 255 is low light level and 0 is high light. 
//
  if (t>=0600 and t<2000){
    //fadeValue = 50;
    fadeValue = high_light_intensity; /// Ve que este' en la intensidad que necesitas
    //fadeValue = 300;
    //NightMode();
  }
  else {
    NightMode(); // In any other case than the ones stated above, no lights!
    //fadeValue = high_light_intensity;
  }
    
// **** FAN ****
//  This section turns the fan On and Off 
   // if (fadeValue == 0) {digitalWrite (IR_outPin , HIGH);}  //Esto es para que el fan este prendido en low-light, si lo quieres en high light cambia el fadeValue a O
 //   else { digitalWrite (IR_outPin , HIGH);}
  delay ( 1000);
}
