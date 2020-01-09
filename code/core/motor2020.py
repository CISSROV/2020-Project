#!/usr/bin/env python3.4
'''Author: Jonathan Rotter

look at motor2020++.py for comments

motor2020++.py features throttling of the vertical thrusters
as the ensuing power surges have cause brown-outs during
the 2019 competition, requiring a full restart of the ROV

This is the old code that does not feature this throttling
And cause I'm lazy and the two files are almost the same,
look at the other one for comments

Required 3rd-party libraries:
`autobahn`
`twisted`
`pyfirmata`
'''

from sys import version
if version[0] != '3':
    raise Exception('This is Python3 code')

import webSocketClient
import json


axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
'''List of axis controls on the XBox controllers'''

buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']
'''List of buttons on the XBox controllers'''

PORT = '/dev/ttyACM0'
'''Location where the Arduino Mega can be found for pyfirmata'''

trimUp = {
    'left': 0.0,
    'right': 0.0
}
'''Stores the default power level of the vertical thrusters.
As the ROV does not have perfect density,
this value can be adjusted by the bumpers (LB, RB) on the controller
to keep the ROV at constant depth when at rest'''

justPressed = [
    {
        'A': False,
        'B': False,
        'X': False,
        'Y': False,
        'LB': False,
        'RB': False
    },
    {
        'A': False,
        'B': False,
        'X': False,
        'Y': False,
        'LB': False,
        'RB': False
    }
]
'''
Stores which buttons are currently pressed
so that code activates only once per
button press and does not repeat
'''

emergencyPower = False
'''Controls whether or not the vertical thrusters
are restrained in their power usage as the
low quality motor controllers make them cause
a voltage drop that can and has caused a brown-out
in the raspberry pis'''

if __name__ == '__main__':
    import pyfirmata

    # setup pyFirmata
    BOARD = pyfirmata.Arduino(PORT)

    # setup an iterator for safety
    iter8 = pyfirmata.util.Iterator(BOARD)
    iter8.start()

    # locate pins
    pins = [
        None,  # no pin 0
        None,  # no pin 1
        BOARD.get_pin('d:2:s'),  # motor 2
        BOARD.get_pin('d:3:s'),  # motor 3
        BOARD.get_pin('d:4:s'),  # motor 4
        BOARD.get_pin('d:5:s'),  # motor 5
        BOARD.get_pin('d:6:s'),  # motor 6 - vertical thruster
        BOARD.get_pin('d:7:s'),  # motor 7 - vertical thruster
        BOARD.get_pin('d:8:s'),  # motor 8 - claw
        BOARD.get_pin('d:9:s'),  # motor 9
        BOARD.get_pin('d:10:s'),  # motor 10
        None,  # no pin 11
        BOARD.get_pin('d:12:s'),  # motor 12
    ]
    '''All pins are put into a list
    so that they can conveniently be referred to
    via pins[pin num]
    example: pins[8].write(150)
    '''


def buttonPressed(button, num):
    '''Specifies what to do if a button is pressed

    Args:
        button (str): The button name: ['A', 'B', 'X', 'Y', 'LB', 'RB']
        num (int): The joystick number, should be either 0 or 1
    '''

    global trimUp, emergencyPower
    # num is zero or one
    if num == 0:
        if button == 'LB':
            trimUp['left'] += 1
            trimUp['right'] += 1
        elif button == 'RB':
            trimUp['left'] -= 1
            trimUp['right'] -= 1
        elif button == 'X':
            emergencyPower = True
        elif button == 'Y':
            emergencyPower = False


def process(data):
    '''Uses a json file of the state of the XBox controller
    to set the motors. The json passed in as `data` must have
    all the labels found in axis and buttons, twice, once
    for each controller. The first twelve are controller 1,
    the second twelve are controller 2

    Args:
        data (str): A json string representing a dict of the controller's state
    '''

    joysticks = json.loads(data)
    assert len(joysticks) == 24  # verify correct count

    joystick1 = dict(zip(axis + buttons, joysticks[:12]))
    joystick2 = dict(zip(axis + buttons, joysticks[12:]))

    old = []  # for debugging

    del data

    global justPressed

    stickNum = 0
    for stick, jPressed in zip((joystick1, joystick2), justPressed):
        for k in stick:
            if k not in buttons:
                continue

            v = stick[k]
            if v == 1 and not jPressed[k]:
                # just pressed
                buttonPressed(k, stickNum)
                jPressed[k] = True
            elif v == 0 and jPressed[k]:
                # just released
                jPressed[k] = False
            elif v not in [1, 0]:
                raise ValueError('Got {0}, expected 0 or 1'.format(v))
            else:
                pass

        stickNum += 1

    del stickNum

    motor_claw = 90

    # print(joystick1)
    if joystick1['A'] and joystick1['B']:
        pass  # do nothing cause both are pressed
    elif joystick1['A']:
        motor_claw = 150
    elif joystick1['B']:
        motor_claw = 30

    # motor setup
    #       150    150
    #       /a/    \b\
    #  4  /////    \\\\\  2
    #
    #               150
    #  5  \\\\\    /////  3
    #      \d\     /c/
    #      150
    # ______________a_b_c_d
    # Back          - - + +
    # Front         + + - -
    # Strafe Left   - + - +
    # Strafe Right  + - + -
    # Rotate Left   - + + -
    # Rotate Right  + - - +
    #

    yLeft = 60 * joystick1['yLeft']
    xLeft = 60 * joystick1['xLeft']  # should be strafe

    global emergencyPower
    if emergencyPower:
        yRight = 60 * joystick1['yRight']
    else:
        yRight = 30 * joystick1['yRight']
        # reduce power to avoid brown outs

    spin = 0

    joystick1['triggerRight'] = (joystick1['triggerRight'] + 1) / 2
    joystick1['triggerLeft'] = (joystick1['triggerLeft'] + 1) / 2

    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2
    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

    if joystick1['triggerRight'] >= 0.1 and joystick1['triggerLeft'] >= 0.1:
        pass  # do nothing cause both are pressed
    else:
        if joystick1['triggerRight'] > 0.1:
            # spin right
            spin = joystick1['triggerRight'] * 60

        if joystick1['triggerLeft'] > 0.1:
            # spin left
            spin = -joystick1['triggerLeft'] * 60

    motor_a = 90 + yLeft - xLeft - spin

    motor_b = 90 + yLeft + xLeft + spin

    motor_c = 90 - yLeft + xLeft - spin

    motor_d = 90 - yLeft - xLeft + spin

    # mixing
    # m1 = 90+forwardval+strafeval+turnval
    # m2 = 90+forwardval-strafeval-turnval
    # m3 = 90-forwardval+strafeval
    # m4 = 90-forwardval-strafeval

    global trimUp

    # motors are not running at 93 instead of 90
    # why? I wish I knew
    motor_up_left = 93 - (trimUp['left'] + yRight)
    motor_up_right = 93 - (trimUp['right'] + yRight)  # thrusters reversed

    def bounds(x):
        '''
        Ensures that 30 <= x <= 150 for the motors
        The motors don't respond to higher or lower values
        Rounds result to three decimal points

        Args:
            x (int): Number to ensure is within 30 to 150

        Returns:
            x: An int that fits 30 <= x <= 150
        '''
        if x < 30:
            return 30
        if x > 150:
            return 150
        return round(x, 3)

    def specialBounds(x):
        '''
        Ensures that 20 <= x <= 210 for the vertical thrusters
        Rounds result to three decimal points

        Args:
            x (int): Number to ensure is within 20 to 210

        Returns:
            x: An int that fits 20 <= x <= 210
        '''
        if x < 20:
            return 20
        if x > 210:
            return 210
        return round(x, 3)

    motor_a = bounds(motor_a)
    motor_b = bounds(motor_b)
    motor_c = bounds(180 - motor_c)  # reverse # de reverse
    motor_d = bounds(motor_d)

    motor_up_left = specialBounds(motor_up_left)
    motor_up_right = specialBounds(motor_up_right)

    # right
    pins[4].write(motor_a)
    pins[2].write(motor_b)
    pins[3].write(motor_c)
    pins[5].write(motor_d)

    # 150 down up, 30 move up
    pins[6].write(motor_up_right)  # stop on 93
    pins[7].write(motor_up_left)  # stop on 93

    pins[8].write(motor_claw)

    # print datalist
    for i in range(30):
        # \r is a special character that makes print
        # start at the beginning of the line, overwritting
        # what is already there
        #
        # \033 is the ascii escape character for special
        # terminal instructions
        # \033[A moves the cursor up a line
        # \033[K clears the line
        # refer to http://ascii-table.com/ansi-escape-sequences.php
        #
        # the point of these are to clear the terminal screen
        print('\r\033[A\033[K', end='')

    print('Trim: [{0}, {1}]'.format(trimUp['left'], trimUp['right']))
    print(joystick1)
    print(joystick2)
    print(motor_a, motor_b)
    print(180-motor_c, motor_d)
    print()
    print(motor_up_left, motor_up_right)
    print(motor_claw)
    # global emergencyPower
    if emergencyPower:
        print('-----------------------')
        print('-- MAX POWER ENABLED --')
        print('-----------------------')

    index = 0
    for i in old:
        print(index, i)
        index += 1


if __name__ == '__main__':
    webSocketClient.start('motor', process, ip="192.168.1.2")
    # assumes that motor pi has ip 192.168.1.2
