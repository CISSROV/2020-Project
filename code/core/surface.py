#!/usr/bin/env python3.4
import webSocketClient
import pygame
import json

axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

pygame.init()

joystick1 = pygame.joystick.Joystick(0)
joystick2 = pygame.joystick.Joystick(1)
joystick1.init()
joystick2.init()

def getData():

    data1 = []

    values = [round(joystick1.get_axis(x), 2) for x in range(6)]
    data1.append(list(zip(axis, values)))

    values = [round(joystick1.get_button(x), 2) for x in range(6)]
    data1.append(list(zip(axis, values)))

    data2 = []

    values = [round(joystick2.get_axis(x), 2) for x in range(6)]
    data2.append(list(zip(axis, values)))

    values = [round(joystick2.get_button(x), 2) for x in range(6)]
    data2.append(list(zip(axis, values)))

    allData = [dict(data1), dict(data2)]
    for i in range(30):
        print ('\r\033[A\033[K', end='')

    print(allData)

    pygame.event.pump()

    return json.dumps(allData)

webSocketClient.start('surface', getData)
