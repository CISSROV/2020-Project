import RPi.GPIO as GPIO
import time

HIGH = GPIO.HIGH
LOW = GPIO.LOW

IN1 = int(input('IN1: ')) #16 # GPIO pin number to IN1
IN2 = int(input('IN2: ')) #26 # GPIO pin number to IN2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)

GPIO.output(IN1, LOW)

p = GPIO.PWM(IN2, 50)
p.start(50)
try:
    while 1:
        # dc is the speed, should be between 0 and 100
        dc = int(input('power: '))
        
        p.ChangeDutyCycle(dc)
        time.sleep(1)
except KeyboardInterrupt:
    print('Stopping!')
finally:
    p.stop()
    GPIO.cleanup()
