#!/usr/bin/env python3.4
import webSocketClient
import motorInterface
import json

axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

trimUp = {
    'left': 0.0,
    'right': 0.0
}

# these are in a row

# this motor is IN3/4 on the edge of the motor controller
m1 = motorInterface.motor(16, 26)
# next to the one above
m2 = motorInterface.motor(12, 13)

# 2nd chip
m3 = motorInterface.motor(27, 23)
m4 = motorInterface.motor(4, 18)

def move1(pow):
    m1.set(pow)

def move2(pow):
    m2.set(pow)

def move3(pow):
    m3.set(pow)

def move4(pow):
    m4.set(pow)

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
    global trimUp
    # num is 0 or 1
    if num == 1:
        if button == 'LB':
            trimUp['left'] += 1
            trimUp['right'] += 1
        elif button == 'RB':
            trimUp['left'] -= 1
            trimUp['right'] -= 1


def process(data):
    joysticks = json.loads(data)
    assert len(joysticks) == 24

    joystick1 = dict(zip(axis + buttons, joysticks[:12]))
    joystick2 = dict(zip(axis + buttons, joysticks[12:]))

    old = [] # for debugging

    #print('msg:', joysticks)

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

    yLeft = 50 * joystick2['yLeft']
    xLeft = 50 * joystick2['xLeft']
    yRight = 50 * joystick2['yRight']
    xRight = 50 * joystick2['xRight']

    spin = 0

    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2
    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2
    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

    if joystick2['triggerRight'] >= 0.1 and joystick2['triggerLeft'] >= 0.1:
        pass # do nothing cause both are pressed
    else:
        if joystick2['triggerRight'] > 0.1:
            # spin right
            spin = joystick2['triggerRight'] * 60

        if joystick2['triggerLeft'] > 0.1:
            # spin left
            spin = -joystick2['triggerLeft'] * 60


    motor_a = yLeft - xLeft - spin

    motor_b = yLeft + xLeft + spin

    motor_c = -yLeft + xLeft - spin

    motor_d = -yLeft - xLeft + spin

    global trimUp

    motor_up_left  = 93 + trimUp['left'] + yRight
    motor_up_right = 93 + trimUp['right'] + yRight

    def bounds(x):
        # max power is -100 to 100
        if x < -50:
            return -50
        if x > 50:
            return 50
        return round(x, 2)

    motor_a = bounds(motor_a)
    motor_b = bounds(motor_b)
    motor_c = bounds(180 - motor_c) # reverse
    motor_d = bounds(motor_d)

    motor_up_left  = bounds(motor_up_left)
    motor_up_right = bounds(motor_up_right)

    
    # right
    move1(motor_a)
    move2(motor_b)
    move3(motor_c) # ================ FIX THIS ================
    move4(motor_d)
    

    # print datalist
    for i in range(30):
        print('\r\033[A\033[K', end='')

    print('Trim: [{0}, {1}]'.format(trimUp['left'], trimUp['right']))
    print(joystick1)
    print(joystick2)
    print(motor_a, motor_b)
    print(motor_c, motor_d)
    print()
    print(motor_up_left, motor_up_right)
    print(motor_claw)
    index = 0
    for i in old:
        print(index, i)
        index += 1

webSocketClient.start('motor', process)
