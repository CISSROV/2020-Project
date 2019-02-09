import RPi.GPIO as GPIO
import time

HIGH = GPIO.HIGH
LOW = GPIO.LOW

IN1 = 21 # GPIO pin number to IN1
IN2 = 20 # GPIO pin number to IN2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)

GPIO.output(IN1, LOW);

p = GPIO.PWM(IN2, 50)
p.start(50)
try:
    while 1:
        # dc is the speed, should be between 0 and 100
        for dc in range(0, 101, 5):
            p.ChangeDutyCycle(dc)
            time.sleep(1)
        print('top')
        for dc in range(100, -1, -5):
            p.ChangeDutyCycle(dc)
            time.sleep(1)
        print('bottom')
except KeyboardInterrupt:
    print('Stopping!')
finally:
    p.stop()
    GPIO.cleanup()
