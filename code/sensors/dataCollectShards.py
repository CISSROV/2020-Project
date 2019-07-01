#!/usr/bin/env python3.4

# For specifying whenever the temperature sensors should be used
# set it to False if it is broken or the wires are disconnected for example
TEMPSENSOR = True

if TEMPSENSOR:
    import tempSensor # contains code for collecting tempSensor data

import time
import json
import os
import sys

# add this path to sys.path so that Adafruit_BNO055 can be imported
sys.path.append('/home/pi/Adafruit_Python_BNO055')

# 3rd-party libary from somewhere on github
from Adafruit_BNO055 import BNO055

# Specify if the data should be printed each time
# it is collected
silent = True

# global variable which will hold an object
bno = None

# for zeroing the gyroscope, these are set when
# the gyro starts up
defaultRotation = {'heading': 0, 'roll': 0, 'pitch': 0}
defaultAcc = {'x': 0, 'y': 0, 'z': 0}

# if the gyro is running, used to message that it needs a reboot
gyroRunning = True

# if the gyro has setup at least once
hasSetupOnce = False

def setup():
    # ---------------------------
    # ---- Gyro Startup Code ----
    # ---------------------------
    global bno, gyroRunning, hasSetupOnce

    # make a BNO055 object representing the gyro
    # No idea what rst is or why it is set to 18
    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

    # Register read errors come after this (for debugging)

    # variables used in gyro setup
    disconnected = False
    failureCount = 0

    # Initialize the BNO055 and stop if something went wrong.
    # Crashes occurs here; Register read error
    while True:
        try:
            # try to start the gyro
            disconnected = not bno.begin()
        except Exception as e:
            # catch an exception and increment the failed start counter
            print(e)

            # wait a bit
            time.sleep(0.1)

            failureCount += 1

            if failureCount > 10:
                # give up after 10 tries
                print('You\'re a failure, just like this code')
                gyroRunning = False

                break # haven't tested if this break statement works
                
        else:
            # all things good on startup
            break

        if disconnected:
            # failed to init the gyro
            print('Failed to initialize BNO055! Is the sensor connected?')
            gyroRunning = False

    # if the gyro managed to start well without crashing
    if gyroRunning:

        # Print system status and self test result.
        status, self_test, error = bno.get_system_status()
        print('System status: {0}'.format(status))
        print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))

        # Print out an error if system status is in error mode.
        if status == 0x01:
            raise RuntimeError('System error: {0}'.format(error) +\
                '\nSee datasheet section 4.3.59 for the meaning.')

        # Print BNO055 software revision and other diagnostic data.
        sw, bl, accel, mag, gyro = bno.get_revision()
        print('Software version:   {0}'.format(sw))
        print('Bootloader version: {0}'.format(bl))
        print('Accelerometer ID:   0x{0:02X}'.format(accel))
        print('Magnetometer ID:    0x{0:02X}'.format(mag))
        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

        if hasSetupOnce:
            # don't get default values again so a reboot doesn't mess up the displayed values
            return 

        # number of measurements to average
        MEASUREMENTS = 10

        # the first few readings tend to be zero so get rid of those
        for i in range(5):
            bno.read_euler()
            bno.read_linear_acceleration()
            time.sleep(0.1)

        global defaultRotation, defaultAcc

        defaultRotation = {'heading': 0, 'roll': 0, 'pitch': 0}
        defaultAcc = {'x': 0, 'y': 0, 'z': 0}

        # take ten measurements and average them

        for i in range(MEASUREMENTS):
            # get orientation
            heading, roll, pitch = bno.read_euler()
            print(heading, roll, pitch, end=' ')

            # sum values, will be divided by the number of measurements later
            defaultRotation['heading'] += heading
            defaultRotation['roll'] += roll
            defaultRotation['pitch'] += pitch

            # linear acceleration
            x, y, z = bno.read_linear_acceleration()
            print(x, y, z)

            # sum values, will be divided by the number of measurements later
            defaultAcc['x'] += x
            defaultAcc['y'] += y
            defaultAcc['z'] += z

            # pause for 100ms
            time.sleep(0.1)

        # divide the sum of readings by the number of measurements to get the average
        defaultRotation['heading'] /= MEASUREMENTS
        defaultRotation['roll'] /= MEASUREMENTS
        defaultRotation['pitch'] /= MEASUREMENTS

        defaultAcc['x'] /= MEASUREMENTS
        defaultAcc['y'] /= MEASUREMENTS
        defaultAcc['z'] /= MEASUREMENTS

        print(defaultAcc)
        print(defaultRotation)

        # for making sure these values aren't altered if the gyro reboots
        hasSetupOnce = True


# ------------------------
# ---- Main Function -----
# ------------------------

def getDataFragment():
    global gyroRunning

    # get the current time
    t = time.localtime()
    t = ':'.join([str(i).zfill(2) for i in [t.tm_hour, t.tm_min, t.tm_sec]])

    # try to get the data from the temperature probe if it is enabled
    try:
        if TEMPSENSOR:
            externalTemp = round(tempSensor.getTemp(), 2)
        else:
            # no temperature probe data
            externalTemp = -1
    except:
        # some error occured
        externalTemp = 'Error'

    try:
        # try to get the core temperature of the raspberry pi
        coreTemp = os.popen('/opt/vc/bin/vcgencmd measure_temp').read()
        coreTemp = round(float(coreTemp[coreTemp.index('=')+1:-3]), 2)
    except:
        # some error occured
        coreTemp = 'Error'

    # Gyro Sensors
    try:
        heading, roll, pitch = bno.read_euler()

        # remove the intial state to get orientation relative to its start point
        heading -= defaultRotation['heading']
        roll -= defaultRotation['roll']
        pitch -= defaultRotation['pitch']

        # round data
        heading = round(heading, 2)
        roll = round(roll, 2)
        pitch = round(pitch, 2)

        # unused
        sys, gyro, accel, mag = bno.get_calibration_status()

        # read magnetic field
        x, y, z = bno.read_magnetometer()

        # take the absolute value of the magnetic field and turn it into gauss
        magField = pow(x ** 2 + y ** 2 + z ** 2, 0.5)
        magField = round(magField / 100, 3) # 100 microTesla = 1 Gauss

        # get linear acceleration
        x, y, z = bno.read_linear_acceleration()

        # for removing strange acceleration picked up when there is none
        # btw read_linear_acceleration() takes out gravity already
        x -= defaultAcc['x']
        y -= defaultAcc['y']
        z -= defaultAcc['z']

        # round data
        x = round(x, 3)
        y = round(y, 3)
        z = round(z, 3)

        # round the temp too
        # this is the temperature of the gyro, which shows internal ROV temperature
        internalTemp = round(bno.read_temp(), 2)

        #
        # all the data will be displayed on an html page so if the 
        # values have too many decimal places it will mess up the html table
        #
    except:
        # exception in getting data

        heading, roll, pitch = 'Error', 'Error', 'Error'
        magField = 'Error'
        x, y, z = 'Error', 'Error', 'Error'
        internalTemp = 'Error'
        gyroRunning = False

    if not gyroRunning:
        # if the gyro has failed try to reboot it
        print('Attempting to restart gyro')

        gyroRunning = True
        setup()

    # assemble the data into a list
    fragment = [t, externalTemp, coreTemp, internalTemp, \
                      heading, roll, pitch, \
                      magField, x, y, z]

    # print the data if allowed
    if not silent:
        print(fragment)

    # return the data
    return fragment
