'''
Author: Jonathan Rotter

Sets the motors used on the mini-rov
on the desired power setting
'''

from sys import stderr

if __name__ == '__main__':
    import RPi.GPIO as GPIO

    # GPIO settings
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
else:
    # this is a dummy module of GPIO
    # so that the auto documenter pdoc3 will shut up
    class GPIO:
        def setup(*args, **kwargs): pass
        def output(*args, **kwargs): pass
        def PWM(*args, **kwargs):
            class PWM:
                def start(*args, **kwargs): pass
            return PWM
        OUT = None
        LOW = None
        HIGH = None


class motor:
    '''
    Provides interface between one motor
    and the rest of the program

    An object of this class should be
    created for each motor
    '''

    motorList = []
    '''
    list of all the connected motors.
    this is a static variable!
    '''

    def __init__(self, IN1, IN2):
        '''
        IN1 and IN2 are the pin numbers
        that the motor is connected to

        Args:
            IN1 (int) pin controlling direction
            IN2 (int): pin controlling power level

        self.IN1 = IN1
        self.IN2 = IN2
        '''

        # setup the pins to be output
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)

        #
        # start up the motors
        # telling them to not spin
        #

        # set direction of motor
        GPIO.output(IN1, GPIO.LOW)

        # make a PWM object that sends pulses on pin IN2,
        # controlling the motor power
        self.p = GPIO.PWM(IN2, 50)  # the 50 was chosen arbitrarily
        # start the PWM
        self.p.start(0)

        # add this instance of the motor class to the static var list
        motor.motorList.append(self)

    def set(self, power):
        '''
        Sets the power level of the motor
        represented by this object.
        A power level of 0 is stop

        Args:
            power (int): Should be from -100 to 100
        '''
        # power should be -100 <= power <= 100
        # 0 is stop

        # check if the argument is within requirements
        if power < -100 or power > 100:
            print('power arg is not norminal: Expected value in range [-100, 100], but got {0}'.format(power), file=stderr)
            return

        # flip the power variable if opposite direction is specified
        # and set the direction based on if the power argument is positive or negative
        direction = 0
        if power < 0:
            direction = 1
            power = 100 + power

        # set the direction
        GPIO.output(self.IN1, direction)
        # set the power level
        self.p.ChangeDutyCycle(power)

    def cleanup(self):
        '''
        Stops the PWM and sets the pins
        to low. The module-level function
        `cleanup` call this method on
        all motor objects
        '''
        # call this when shutting down
        GPIO.output(self.IN1, GPIO.LOW)
        # stop the PWM
        self.p.stop()


def cleanup():
    '''
    Stops the PWM and sets the pins
    to low for all motors. Should be called when the program
    terminates.
    '''
    try:
        # try to shutdown each motor in the list of motors
        for motorObj in motor.motorList:
            motorObj.cleanup() 
    finally:
        # call this no matter what happens / crashes to cleanup the GPIO pins
        GPIO.cleanup()


if __name__ == '__main__':
    # not to be called, supporting module
    raise Exception('This module should only be imported')
