#!/usr/bin/env python3.4
'''Author: Jonathan Rotter

Motor control featuring toggglable throttling of the vertical
thrusters as they have caused brown outs in motor pi

This code is meant to be run on motor pi and requires
a connected arduino mega

The ip of server pi must be specified in the
webSocketClient.start call at the bottom of this file
port is 8008 and is specified in webSocketClient.py

Required 3rd-party libraries:
`autobahn`
`twisted`
`pyfirmata`
'''

# Check if the version of python is 3.x
from sys import version
if version[0] != '3':
    # Stop running if the version is python 2.x
    raise Exception('This is Python3 code')

import webSocketClient
import json

axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']
'''Data labels for axis and buttons in the order
specified by `joystick config.md`
'''

PORT = '/dev/ttyACM0'
'''Port that the arduino mega is connected to'''

# Trim values
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
        # 1st joystick
        'A': False,
        'B': False,
        'X': False,
        'Y': False,
        'LB': False,
        'RB': False
    },
    {
        # 2nd Joystick
        'A': False,
        'B': False,
        'X': False,
        'Y': False,
        'LB': False,
        'RB': False
    }
]
'''Stores if a button was just pressed to ensure buttons are only processed
once per press.
Changed to true once pressed and false once released'''

emergencyPower = False
'''Specifies if the vertical thrusters are throttled to
prevent power surges causing voltage drops or not'''

currentPower = {
    'left': 93.0,
    'right': 93.0
}
'''Current power level sent to the vertical thrusters'''

import pyfirmata

# Setup pyFirmata
BOARD =  pyfirmata.Arduino(PORT)

# Setup an iterator for safety (no idea what that means, ask Danny or Yilou)
iter8 = pyfirmata.util.Iterator(BOARD)
iter8.start()

# Setup pins
pins = [
    None, # no pin 0
    None, # no pin 1
    BOARD.get_pin('d:2:s'), #motor 2
    BOARD.get_pin('d:3:s'), #motor 3
    BOARD.get_pin('d:4:s'), #motor 4
    BOARD.get_pin('d:5:s'), #motor 5
    BOARD.get_pin('d:6:s'), #motor 6 - vertical thruster
    BOARD.get_pin('d:7:s'), #motor 7 - vertical thruster
    BOARD.get_pin('d:8:s'), #motor 8 - claw
    BOARD.get_pin('d:9:s'), #motor 9
    BOARD.get_pin('d:10:s'), #motor 10
    None, # no pin 11
    BOARD.get_pin('d:12:s'), #motor 12
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

    # Check if it received a valid button
    if button not in buttons:
        raise KeyError('Unknown button {}'.format(button))

    global trimUp, emergencyPower

    # If it is the 1st joystick
    if num == 0:
        if button == 'LB':
            # Trim up
            trimUp['left'] += 1
            trimUp['right'] += 1

        elif button == 'RB':
            # Trim down
            trimUp['left'] -= 1
            trimUp['right'] -= 1

        elif button == 'X':
            # Disable throttling
            emergencyPower = True

        elif button == 'Y':
            # Enable throttling
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

    global emergencyPower, justPressed

    # Load json string into a list
    joysticks = json.loads(data)
    # Verify the number of entries of the list
    assert len(joysticks) == 24

    # Use the labels to make a dictionary
    # with the keys being labels and values being the joystick values
    joystick1 = dict(zip(axis + buttons, joysticks[:12]))
    joystick2 = dict(zip(axis + buttons, joysticks[12:]))

    old = []  # for debugging

    del data

    # stick is a dict representing one of the joysticks
    # jPressed is a dict found in justPressed
    # stickNum is either 0 or 1 and is used as an argument in buttonPressed()
    #
    # This for loop is for processing button presses
    for stick, jPressed, stickNum in zip((joystick1, joystick2), justPressed, range(2)):
        for k in stick:
            if k not in buttons:
                continue  # only processes button presses, not axis

            # value of button, which is 0 or 1
            v = stick[k]
            if v == 1 and not jPressed[k]:
                # button was just pressed
                buttonPressed(k, stickNum)
                jPressed[k] = True

            elif v == 0 and jPressed[k]:
                # button was just released
                jPressed[k] = False

            elif v not in [1, 0]:
                # Got a value other than 0 or 1 for the state of a button
                raise ValueError('Got {0}, expected 0 or 1'.format(v))

            else:
                pass  # nothing to do

    motor_claw = 90

    # 'A' and 'B' open and close the claw
    if joystick1['A'] and joystick1['B']:
        pass  # do nothing because both are pressed

    elif joystick1['A']:
        motor_claw = 150  # open or close it

    elif joystick1['B']:
        motor_claw = 30  # open or close it

    #   Motor positioning
    #
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

    # the joystick values are from -1 to 1
    # scale them to be from -60 to 60
    yLeft = 60 * joystick1['yLeft']
    xLeft = 60 * joystick1['xLeft']  # should be strafe
    yRight = 60 * joystick1['yRight']

    # Code for rotating the ROV

    spin = 0

    # Change the values to be from 0 to 1 instead of from -1 to 1
    joystick1['triggerRight'] = (joystick1['triggerRight'] + 1) / 2
    joystick1['triggerLeft'] = (joystick1['triggerLeft'] + 1) / 2

    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2
    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

    if joystick1['triggerRight'] >= 0.1 and joystick1['triggerLeft'] >= 0.1:
        pass  # do nothing because both are pressed

    else:
        # axis don't go perfectly to zero so the
        # if statement is used to make sure the trigger is actually pressed
        if joystick1['triggerRight'] > 0.1:
            # spin right
            spin = joystick1['triggerRight'] * 60

        if joystick1['triggerLeft'] > 0.1:
            # spin left
            spin = -joystick1['triggerLeft'] * 60

    # mixing motor values
    motor_a = 90 + yLeft - xLeft - spin

    motor_b = 90 + yLeft + xLeft + spin

    motor_c = 90 - yLeft + xLeft - spin

    motor_d = 90 - yLeft - xLeft + spin

    global trimUp

    neutral_up = 93  # the motors and escs are weird

    motor_up_left = neutral_up - (trimUp['left'] + yRight)
    motor_up_right = neutral_up - (trimUp['right'] + yRight)

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

    # keep motor values within bounds
    motor_a = bounds(motor_a)
    motor_b = bounds(motor_b)
    motor_c = bounds(180 - motor_c)  # reverse due to how it was connected
    motor_d = bounds(motor_d)

    motor_up_left = specialBounds(motor_up_left)
    motor_up_right = specialBounds(motor_up_right)

    # Vertical thruster throttling to try to avoid power surges
    step = 5

    if emergencyPower:
        # No throttling
        # Changes in control take immediate effect
        currentPower['left'] = motor_up_left
        currentPower['right'] = motor_up_right

    else:
        if neutral_up == motor_up_left:
            # Turn thruster off immediately
            currentPower['left'] = motor_up_left

        else:
            # Change thruster power slowly to avoid current spikes

            if currentPower['left'] < motor_up_left:  # less than desired
                # increase the thruster value by a bit
                currentPower['left'] += step

                # check if the step went beyond the desired power value
                # if so, set it back
                if currentPower['left'] > motor_up_left:
                    currentPower['left'] = motor_up_left

            if currentPower['left'] > motor_up_left:  # more than desired
                # decrease the thruster value by a bit
                currentPower['left'] -= step

                # check if the step went beyond the desired power value
                # if so, set it back
                if currentPower['left'] < motor_up_left:
                    currentPower['left'] = motor_up_left

        if neutral_up == motor_up_right:
            # Turn thruster off immediately
            currentPower['right'] = motor_up_right

        else:
            # Change thruster power slowly to avoid current spikes

            if currentPower['right'] < motor_up_right:  # less than desired
                # increase the thruster value by a bit
                currentPower['right'] += step

                # check if the step went beyond the desired power value
                # if so, set it back
                if currentPower['right'] > motor_up_right:
                    currentPower['right'] = motor_up_right

            if currentPower['right'] > motor_up_right:  # more than desired
                # decrease the thruster value by a bit
                currentPower['right'] -= step

                # check if the step went beyond the desired power value
                # if so, set it back
                if currentPower['right'] < motor_up_right:
                    currentPower['right'] = motor_up_right

    # Write data values to the pins aka motors
    pins[4].write(motor_a)
    pins[2].write(motor_b)
    pins[3].write(motor_c)
    pins[5].write(motor_d)

    # 150 down up, 30 move up
    pins[6].write(currentPower['right'])  # stop on 93
    pins[7].write(currentPower['left'])  # stop on 93

    pins[8].write(motor_claw)

    # clear screen
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

    # print datalist info
    print('Trim: [{0}, {1}]'.format(trimUp['left'], trimUp['right']))
    print(joystick1)
    print(joystick2)
    print(motor_a, motor_b)
    print(180-motor_c, motor_d)
    # motor_c is reversed so it is re-reversed here
    print()
    print(currentPower['left'], currentPower['right'])
    print(motor_claw)

    if emergencyPower:
        print('-----------------------')
        print('-- MAX POWER ENABLED --')
        print('-----------------------')

    # for debugging
    for index, i in enumerate(old):
        print(index, i)

# start a web socket client
# type is "motor", handling function is process
# ip is that of the server
webSocketClient.start('motor', process, ip="192.168.1.2")
