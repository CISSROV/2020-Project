
#include "Keyboard.h"

/*
 * Code for entering all keystrokes necessary to start the ROV.
 * 
 * Needs to be uploaded on an Arduino Mirco or Arduino Leonardo
 * as those are the only ones that can emulate a Keyboard
 * and cause keystrokes to be sent to the computer
 * 
 * How to use:
 *  plug the Arduino into the computer once the computer
 *  is up and running
 *  Uses Raspian-specific keystroke shortcuts
 */

char ctrlKey = KEY_LEFT_CTRL;
char otherKey = KEY_LEFT_ALT;

/*
 * Keyboard shortcut for opening a new tab 
 * in the Terminal in Raspian Linux
 */
void newTab() {
  Keyboard.press(ctrlKey);
  Keyboard.press('T');
  delay(100);
  Keyboard.releaseAll();
  delay(200);
}

/*
 * Enter a command on the Terminal
 * and press enter
 * 
 * s: the command to enter
 */
void runCmd(String s) {
  Keyboard.println(s);
  delay(100);
}

/*
 * Starts the setup sequence
 * 1 second after the Arduino
 * starts up.
 */
void setup() {
  // put your setup code here, to run once:
  Keyboard.begin();
  delay(1000);  
  
  Keyboard.press(ctrlKey);
  Keyboard.press(otherKey);
  Keyboard.press('t');
  delay(100);
  Keyboard.releaseAll();

  delay(2000);

  runCmd("python3 ~/server2020.py");
  newTab();

  runCmd("python3 ~/surface2020.py");
  newTab();


  runCmd("ssh pi@192.168.1.4"); // motorPI
  delay(500);
  runCmd("raspberry");
  delay(1000);
  runCmd("python3 ~/motor2020.py");
  
  newTab();

  runCmd("ssh pi@192.168.1.3"); // cameraPI
  delay(500);
  runCmd("raspberry");
  delay(1000);
  runCmd("sudo python3.4 /var/www/scripts/webSocketServer.py");

  
}

void loop() {
  // unused
}
