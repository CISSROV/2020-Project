#!/usr/bin/env python3.4
# Author: Jonathan Rotter

# Check if the version of python is 3.x
from sys import version
if version[0] != '3':
    # Stop running if the version is python 2.x 
    raise Exception('This is Python3 code')

import webSocketClient
import pygame
import json

#axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
#buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

pygame.init()

# Setup joysticks
joysticks = [pygame.joystick.Joystick(i) for i in range(2)]

for stick in joysticks:
    stick.init() # do we need this?


def getData():
    #
    # gets the data from the joysticks and returns it
    #

    global joysticks

    def dealWithNumber(n):
        # as axis usually don't return to perfect zero, this removes noise
        if abs(n) < 0.1:
            return 0
        return round(n, 2)

    allData = []

    for i in range(2):
        # add every axis and button to a list after sending the values through dealWithNumber()
        # order: [axis0, axis1, axis2, axis3, axis4, axis5, button0, button1, button2, button3, button4, button5]
        allData.append([dealWithNumber(joysticks[i].get_axis(x), 2) for x in range(6)] \
            + [dealWithNumber(joysticks[i].get_button(x), 2) for x in range(6)])

    # clear screen
    for i in range(30):
        # '\r' moves to the start of the line
        # '\033[A' moves up one line
        # '\033[K' clears the line
        print('\r\033[A\033[K', end='')

    # print data
    print(allData)

    pygame.event.pump() # don't what this is. Ask Danny or Yilou but I doubt they know either

    return json.dumps(allData) # returns values as json string

# start a web socket client
# type is "surface", handling function is getData
webSocketClient.start('surface', getData)
