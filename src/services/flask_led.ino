#include "FastLED.h"

// DEFINES
#define NUM_LEDS 300  // Total number of LEDs on the strip
#define DATA_PIN 9    // Data pin

// Vars for each program (subject to change)
const int BUFF_SIZE = 72;
char msgBuffer[BUFF_SIZE];
const int endOfMsgSize = 2;
int endOfMsg[endOfMsgSize] = {42, 42};

unsigned int old_state = 0;
unsigned int old_hue = 150;
unsigned int old_brightness = 0;

// Setting up LED struct
CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);
  Serial.begin(9600);

  // Read init from LED service
  bool init_flag = false;
  int sizeInitResp = 0;
  const int goodInitMsgSize = 6;
  char goodInitMsg[goodInitMsgSize] = {105, 110, 105, 116, 42, 42};
  while (!init_flag) {
    if (Serial.available() > 0) {
      sizeInitResp = readAvailBytes(msgBuffer);

      char initMsg[sizeInitResp];
      for (int i = 0; i < sizeInitResp; ++i) {
        initMsg[i] = msgBuffer[i];
      }

      if (compareCharArrays(initMsg, sizeInitResp, goodInitMsg, goodInitMsgSize)) {
        init_flag = true;
        Serial.print("INITIATED");
      }
      else {
        Serial.print("NOT_INITIATED");
      }
    }
    
    delay(100);
  }
}

// For printing char arrays when they are used to read in Serial data
// Have to pass the size because arrays always end up only being two in length when passed as a paramter for some reason
void printCharArray(char charArray[], int charArraySize, bool printNL) {
  for (int i = 0; i < charArraySize; ++i) {
    Serial.print(charArray[i]);
  }
  if (printNL) {
    Serial.println(); 
  }
}

// For comparing char arrays
bool compareCharArrays(char arr1[], int sizeArr1, char arr2[], int sizeArr2) {
  if (sizeArr1 != sizeArr2) {
    return false;  
  }

  for (int i = 0; i < sizeArr1; ++i) {
    if (arr1[i] != arr2[i]) {
      return false;
    }
  }
  return true;
}

// Check good message
// Ensure the message ends with the accepted endOfMsg values
bool checkGoodMsg(char msg[], int msgSize) {
  // For if the message is shorter than the endOfMsg pattern
  if (msgSize < endOfMsgSize) return false;
  for (int i = 0; i < endOfMsgSize; ++i) {
    if (msg[msgSize - (endOfMsgSize - i)] != endOfMsg[i]) return false;
  }
  return true;
}


bool checkMsgLength(char msg[], int msgSize) {
  bool check = true;
  char msgLen[2] = {msg[msgSize-4], msg[msgSize-3]};
  unsigned long msgLenUL = strtoul(msgLen, NULL, 16);
  if (msgSize != msgLenUL) {
    // Serial.println("Expecting size " + String(msgSize) + ", got " + String(msgLenUL));
    return !check;
  }
  return check;
}

// The Serial.readBytesUntil will read more than one instance of the delimiter, hard to explain but I don't like it
// NOTE: This is broken. If the delimeter shows up in the 3 and 5 spot of a read, this will still return as if it found the delimeter
// Best to use readAvailBytes and then check the end of it for the delimeter
// Need to work on this
int newReadBytesUntil(int delimeter[], char buff[]) {
  int numBytesRead = 0;
  int check = delimeter[0] + 1;
  int numDelimiter = 0;
  while (Serial.available() > 0) {
    check = Serial.read();
    buff[numBytesRead++] = check;
    if (check == delimeter[numDelimiter]) {
      ++numDelimiter;
      if (numDelimiter == sizeof(delimeter)) {
        break;
      }
    }
  }
  return numBytesRead;
}

// Read all currently available bytes
int readAvailBytes(char buff[]) {
  int numBytesRead = 0;
  while (Serial.available() > 0) {
    buff[numBytesRead++] = Serial.read();
  }
  return numBytesRead;
}

void updateLEDHue(int new_hue) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CHSV(new_hue, 255, old_brightness);
  }
  FastLED.show();
}

void updateLEDBrightness(int new_brightness) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CHSV(old_hue, 255, new_brightness);
  }
  FastLED.show();
}

void updateLEDState(unsigned int state) {
  if (state == 0) {
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CHSV(0, 0, 0);
    }
  }
  else {
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CHSV(old_hue, 255, old_brightness);
    }    
  }
  FastLED.show();   
}

void loop() {
  delay(1000);
  if (Serial.available() > 0) {

    // int msgSize = readAvailBytes(msgBuffer);
    int msgSize = newReadBytesUntil(endOfMsg, msgBuffer);

    char msg[BUFF_SIZE];
    for (int i = 0; i < msgSize; ++i) {
      msg[i] = msgBuffer[i];
    }

    if (checkGoodMsg(msg, msgSize) && checkMsgLength(msg, msgSize)) {
      Serial.print("Message recieved: ");
      printCharArray(msg, msgSize, false);
      // Print rest of messsage
      char pad[BUFF_SIZE-msgSize-20]; // 20 is "Message recieved: " + carriage return + new line
      int padSize = sizeof(pad);
      for (int i = 0; i < padSize; ++i) {
        pad[i] = 46;
      }
      printCharArray(pad, padSize, true);
      int indx = 0;
      int numNum = 0;
      bool numFlag = false;
      String val = "";
      int valInt = 0;
      unsigned int current_state;
      unsigned int current_hue;
      unsigned int current_brightness;
      while (indx < msgSize-endOfMsgSize) {
        if (msg[indx] > 47 && msg[indx] < 58) {
          val += msg[indx];
          numFlag = true;
        }
        else {
          if (numFlag){
            ++numNum;
            if (numNum == 1) {
              current_state = val.toInt();
            }
            else if (numNum == 2) {
              current_hue = val.toInt();
            }
            else if (numNum == 3u) {
              current_brightness = val.toInt();
            }
            val = "";
            numFlag = false;
          }
        }
        ++indx;
      }     

      // Check old values against new ones
      if (current_state != old_state) {
        old_state = current_state;
        updateLEDState(current_state);
      }
      if (current_hue != old_hue) {
        old_hue = current_hue;
        updateLEDHue(current_hue);
      }
      if (current_brightness != old_brightness) {
        old_brightness = current_brightness;
        updateLEDBrightness(current_brightness);
      }
    }
    else {
      Serial.print("Receieved bad message: ");
      printCharArray(msg, msgSize, true);
    }
  }
}
