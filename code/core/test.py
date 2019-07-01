#!/usr/bin/env python3.4
# Author: Jonathan Rotter & Danny Kong & Yiluo Li

import time
import pyfirmata

# idk what this is
port = '/dev/ttyACM0'

# Setup pyFirmata
board =  pyfirmata.Arduino(port)

# Setup an iterator for safety
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

# Locate pins
pin2 = board.get_pin('d:2:s') 
pin3 = board.get_pin('d:3:s') 
pin4 = board.get_pin('d:4:s')
pin5 = board.get_pin('d:5:s')
pin6 = board.get_pin('d:6:s')
pin7 = board.get_pin('d:7:s')
pin8 = board.get_pin('d:8:s')
pin9 = board.get_pin('d:9:s')
pin10 = board.get_pin('d:10:s')
pin12 = board.get_pin('d:12:s')

# functions for setting pins
def move2(a):
    pin2.write(a) # motor

def move3(a):
    pin3.write(a) # motor

def move4(a):
    pin4.write(a) # motor

def move5(a):
    pin5.write(a) # motor

def move6(a):
    pin6.write(a) # vertical thruster

def move7(a):
    pin7.write(a) # vertial thruster

def move8(a):
    pin8.write(a)

def move9(a):
    pin9.write(a)

def move10(a):
    pin10.write(a)

def move12(a):
    pin12.write(a)

# main loop
while True:
    # motor number is the pin number the motor is connected to
    # must be an integer otherwise it will crash
    n = int(input('Motor number: '))
    # usually between 30 - 130? I think?
    # motors won't work when set to the extremes of 0, 180
    d = int(input('Power Level: '))
    if n == 2:
        move2(d)
    elif n == 3:
        move3(d)
    elif n == 4:
        move4(d)
    elif n == 5:
        move5(d)
    elif n == 6:
        move6(d)
    elif n == 7:
        move7(d)
    elif n == 8:
        move8(d)
    elif n == 9:
        move9(d)
    elif n == 10:
        move10(d)
    elif n == 12:
        move12(d)
    
    # wait five seconds for some reason
    time.sleep(5)
