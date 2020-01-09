#!/usr/bin/env python3.4
import webSocketClient
import motorInterface
import json

# axis and button labels
axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

# trim to adjust for buoyancy of the miniROV
trimUp = {
    'center': 0.0
}

# don't know what that means
#   ||
#   \/
# these are in a row


# this motor is IN3/4 on the edge of the motor controller
# these pins are based on how the 2019 miniROV was wired up
m1 = motorInterface.motor(16, 26) # vertical
m2 = motorInterface.motor(12, 13) # unused

# 2nd motor controller
m3 = motorInterface.motor(27, 23) # side (maybe left)
m4 = motorInterface.motor(4, 18) # side (maybe right)

# functions for no real reason
def move1(pow):
    m1.set(pow)


def move2(pow):
    m2.set(pow)


def move3(pow):
    m3.set(pow)


def move4(pow):
    m4.set(pow)

# Used to keep track when a button is pressed and when released
# so that functions won't fire twice from one button press
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

def buttonPressed(button, num):
    # this function is called whenever a button is pressed,
    # any button releated features should be added here
    global trimUp
    # num is 0 or 1, representing if it's the first or second xbox controller

    # 0 is 1st controller
    # 1 is 2nd controller

    # LB and RB are used to set the trim of the miniROV
    if num == 1: # 2nd controller
        if button == 'LB':
            trimUp['center'] += 1 # trim up when LB is pressed
        elif button == 'RB':
            trimUp['center'] -= 1 # trim down when RB is pressed



def process(data):
    # this function processes received joystick data

    # turn the data json string into a list 
    # data contains the value of the joysticks buttons/axis
    joysticks = json.loads(data)
    # make sure it has the right number of buttons/axis
    assert len(joysticks) == 24

    # axis and buttons are the labels

    # match up the labels with the data values to make a dictionary
    joystick1 = dict(zip(axis + buttons, joysticks[:12]))
    joystick2 = dict(zip(axis + buttons, joysticks[12:]))

    old = [] # for debugging

    del data

    global justPressed

    stickNum = 0
    # for each xbox controller
    # (joystick1, joystick2) is a tuple of two dicts
    # justPressed is a list of two dicts
    for stick, jPressed in zip((joystick1, joystick2), justPressed):
        # stick is a dictionary containing the labels and values of each button/axis on
        # one of the joysticks

        # jPressed is one of the dictionaries from the justPressed list

        # for every button/axis on this xbox controller
        for k in stick:
            # k is the button/axis label

            # ignore axis
            if k not in buttons:
                continue

            # v is the value of button k
            v = stick[k]

            # if button k is pressed and wasn't pressed already
            if v == 1 and not jPressed[k]:
                # process that this button was just pressed
                buttonPressed(k, stickNum)

                # 
                # Update jPressed so that buttonPressed() 
                # won't fire twice for one button press
                # 
                jPressed[k] = True

            # if button k is not pressed but it was pressed before
            elif v == 0 and jPressed[k]:
                # Button k was just released

                # Update that jPressed is no longer pressed
                # so that buttonPressed() will activate again if it is pressed again
                jPressed[k] = False

            # if button k has a value other than the normal 0 or 1
            elif v not in [1, 0]:
                # should never happen
                raise ValueError('Got {0}, expected 0 or 1'.format(v))

            # if button k hasn't changed status
            else:
                pass

        # add one to stickNum
        # it is needed for buttonPressed()
        stickNum += 1

    del stickNum

    # for mixing controls
    yLeft = 50 * joystick2['yLeft']
    yRight = 50 * joystick2['yRight']

    # triggerRight and triggerLeft have values of -1 to +1,
    # so adjust them to be 0 to +1
    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2
    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

    # vertical power level
    vertical = 0

    if joystick2['triggerRight'] >= 0.1 and joystick2['triggerLeft'] >= 0.1:
        pass # do nothing cause both are pressed
    else:
        # the axis might not go to exact 0 so the if statements try to cut it out

        if joystick2['triggerRight'] > 0.1:
            vertical = joystick2['triggerRight'] * 50

        if joystick2['triggerLeft'] > 0.1:
            vertical = -joystick2['triggerLeft'] * 50


    # Mini-ROV motor setup
    #   top view
    #     ____
    #    |    |
    # /a\|    |/b\
    #    |____|
    #     (up)
    #

    motor_a = yLeft

    motor_b = yRight

    global trimUp

    # add the trim to the vertical power level
    motor_up = trimUp['center'] + vertical

    
    def bounds(x):
        # makes sure that values stay between -50 to 50
        # max power is -100 to 100
        if x < -50:
            return -50
        if x > 50:
            return 50

        # round the result just to have cleaner decimals
        return round(x, 2)

    # make sure each is within allowed bounds
    motor_a = bounds(motor_a)
    motor_b = bounds(motor_b)
    motor_up = bounds(motor_up)
    
    # set the motors
    # which motor is which depends on the wiring of the miniROV
    # This is set to the wiring of the 2019 miniROV
    move1(motor_up)
    move4(motor_a)
    move3(motor_b)

    # -----   print information   -----

    # clear the console window
    for i in range(30):
        # \r goes the the front of the line on the console
        # \033[A goes up a line
        # \033[K clears the line
        print('\r\033[A\033[K', end='')

    # display trim
    print('Trim: {0}'.format(trimUp['center']))
    # display joystick values
    print(joystick1)
    print(joystick2)
    # display power levels
    print(motor_a, motor_b)
    print(motor_up)
    print()

    #
    # for debugging
    # anything added to the old list will be printed here
    #
    # !!! IMPORTANT FOR DEBUGGING !!!
    # because of the screen clearing,
    # nothing printed before it will actually be visible
    # as it will be deleted by the screen clearing.
    # thus, any debug info to pring must be added to old
    # so that it is printed here after the screen clearing
    #
    index = 0
    for i in old:
        print(index, i)
        index += 1

# start the code
# ip should be of the surface pi
# type is 'miniROV'
webSocketClient.start('miniROV', process, ip="192.168.1.2")
