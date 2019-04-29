#!/usr/bin/env python3.4

from sys import version
if version[0] != '3':
    raise Exception('This is Python3 code')

import webSocketClient
import pygame
import json

#axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
#buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

pygame.init()

joysticks = [pygame.joystick.Joystick(i) for i in range(2)]

'''
joystick1 = pygame.joystick.Joystick(0)
joystick2 = pygame.joystick.Joystick(1)
joystick1.init()
joystick2.init()
'''

def getData():
    global joysticks

    def dealWithNumber(n):
        if abs(n) < 0.1:
            return 0
        return round(n, 2)

    allData = []

    for i in range(2):
        allData.append([dealWithNumber(joysticks[i].get_axis(x), 2) for x in range(6)] \
            + [dealWithNumber(joysticks[i].get_button(x), 2) for x in range(6)])

    '''
    tmp = [round(joystick1.get_axis(x), 2) for x in range(6)]
    for i in tmp:
        if abs(i) < 0.1:
            i = 0
        allData.append(i)

    #data1 += list(zip(axis, values))

    allData += [round(joystick1.get_button(x), 2) for x in range(6)]
    #sdata1 += list(zip(buttons, values))

    #data2 = []

    tmp = [round(joystick2.get_axis(x), 2) for x in range(6)]
    for i in tmp:
        if abs(i) < 0.1:
            i = 0
        allData.append(i)
    #data2 += list(zip(axis, values))

    allData += [round(joystick2.get_button(x), 2) for x in range(6)]
    #data2 += list(zip(buttons, values))
    '''

    #allData = [dict(data1), dict(data2)]
    for i in range(30):
        print('\r\033[A\033[K', end='')

    print(allData)

    pygame.event.pump()

    return json.dumps(allData)

webSocketClient.start('surface', getData)
