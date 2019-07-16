
#include "Keyboard.h"

char ctrlKey = KEY_LEFT_CTRL;
char otherKey = KEY_LEFT_ALT;

void newTab() {
  Keyboard.press(ctrlKey);
  Keyboard.press('T');
  delay(100);
  Keyboard.releaseAll();
  delay(200);
}

void runCmd(String s) {
  Keyboard.println(s);
  delay(100);
}

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
  // put your main code here, to run repeatedly:

}
