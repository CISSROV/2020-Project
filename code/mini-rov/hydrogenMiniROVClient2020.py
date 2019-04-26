#!/usr/bin/env python3.4
import webSocketClient
import motorInterface
import json

axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

trimUp = {
    'center': 0.0
}

# these are in a row

# this motor is IN3/4 on the edge of the motor controller
m1 = motorInterface.motor(16, 26) # vertical
m2 = motorInterface.motor(12, 13) # unused

# 2nd chip
m3 = motorInterface.motor(27, 23) # side (maybe left)
m4 = motorInterface.motor(4, 18) # side (maybe right)

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
    if num == 1: # controller number 2
        if button == 'LB':
            trimUp['center'] += 1
        elif button == 'RB':
            trimUp['center'] -= 1


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
    #xLeft = 50 * joystick2['xLeft']
    yRight = 50 * joystick2['yRight']
    #xRight = 50 * joystick2['xRight']

    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2
    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

    vertical = 0

    if joystick2['triggerRight'] >= 0.1 and joystick2['triggerLeft'] >= 0.1:
        pass # do nothing cause both are pressed
    else:
        if joystick2['triggerRight'] > 0.1:
            # spin right
            vertical = joystick2['triggerRight'] * 50

        if joystick2['triggerLeft'] > 0.1:
            # spin left
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
    motor_up = trimUp['center'] + vertical

    
    def bounds(x):
        # max power is -100 to 100
        if x < -50:
            return -50
        if x > 50:
            return 50
        return round(x, 2)

    motor_a = bounds(motor_a)
    motor_b = bounds(motor_b)
    motor_up = bounds(motor_up)
    
    # right
    move1(motor_up)
    move4(motor_a)
    move3(motor_b)

    # print datalist
    for i in range(30):
        print('\r\033[A\033[K', end='')

    print('Trim: {0}'.format(trimUp['center']))
    print(joystick1)
    print(joystick2)
    print(motor_a, motor_b)
    print(motor_up)
    print()
    index = 0
    for i in old:
        print(index, i)
        index += 1

webSocketClient.start('miniROV', process, ip="192.168.1.2")
