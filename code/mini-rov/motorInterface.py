import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#### ----  motor class  ---- ####
# contains info for one motor and a method to set the motor

class motor:
    motorList = []

    def __init__(self, IN1, IN2):
        # IN1 and IN2 are pin numbers
        self.IN1 = IN1
        self.IN2 = IN2

        GPIO.setup(IN1,GPIO.OUT)
        GPIO.setup(IN2,GPIO.OUT)

        # start up
        GPIO.output(IN1, GPIO.LOW)
        self.p = GPIO.PWM(IN2, 50)
        self.p.start(0)

        motor.motorList.append(self)

    def set(self, power):
        # motor should be type RPi.GPIO.PWN
        # power should be -100 <= power <= 100
        if power < -100 or power > 100:
            print('power arg is not norminal: Expectd in range [0, 100], but got {0}'.format(direction), file=stderr)
            return

        direction = 0
        if power < 0:
            direction = 1
            power = 100 + power

        GPIO.output(self.IN1, direction)
        self.p.ChangeDutyCycle(power)

    def cleanup(self):
        # call this when shutting down
        GPIO.output(self.IN1, GPIO.LOW)
        self.p.stop()


def cleanup():
    try:
        for motorObj in motor.motorList:
            motorObj.cleanup() 
    finally:
        GPIO.cleanup()
    
    
if __name__ == '__main__':
    raise Exception('This module should only be imported')


