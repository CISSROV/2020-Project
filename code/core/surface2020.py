#!/usr/bin/env python3.4
'''Author: Jonathan Rotter

Gets the state of the XBox controller
and passes it on to the server
which relays it to motor pi

Required 3rd-party libraries:
`autobahn`
`twisted`
`pygame`
'''

# Check if the version of python is 3.x
from sys import version
if version[0] != '3':
    # Stop running if the version is python 2.x
    raise Exception('This is Python3 code')

import webSocketClient
import pygame
import json

# axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
# buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

pygame.init()

# Setup joysticks
joysticks = [pygame.joystick.Joystick(i) for i in range(2)]
'''Represents the XBox controllers'''

for stick in joysticks:
    stick.init()  # do we need this?


def getData():
    '''
    Gets the data from the joysticks and returns it

    Returns:
        data: json-encoded state of the controllers
    '''

    global joysticks

    def dealWithNumber(n):
        '''Removes noise as axis usually don't return to perfect zero'''
        if abs(n) < 0.1:
            return 0
        return round(n, 2)

    allData = []

    for i in range(2):
        # add every axis and button to a list after sending the values through dealWithNumber()
        # order: [axis0, axis1, axis2, axis3, axis4, axis5, button0, button1, button2, button3, button4, button5]
        allData.append([dealWithNumber(joysticks[i].get_axis(x), 2) for x in range(6)]
            + [dealWithNumber(joysticks[i].get_button(x), 2) for x in range(6)])

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

    # print data
    print(allData)

    # don't know what this is. Ask Danny or Yilou, but I doubt they know either
    pygame.event.pump()

    return json.dumps(allData)  # returns values as json string

# start a web socket client
# type is "surface", handling function is getData
webSocketClient.start('surface', getData)
