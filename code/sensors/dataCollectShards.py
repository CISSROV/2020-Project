#!/usr/bin/env python3.4
TEMPSENSOR = True
if TEMPSENSOR:
    import tempSensor # temp sensor doesn't work
import time
import json
import os
import sys

sys.path.append('/home/pi/Adafruit_Python_BNO055')
from Adafruit_BNO055 import BNO055

silent = True

bno = None

defaultRotation = {'heading': 0, 'roll': 0, 'pitch': 0}
defaultAcc = {'x': 0, 'y': 0, 'z': 0}

gyroRunning = True

def setup():
    # ---------------------------
    # ---- Gyro Startup Code ----
    # ---------------------------
    global bno

    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

    # Register read errors come after this

    disconnected = False
    failureCount = 0
    # Initialize the BNO055 and stop if something went wrong.
    # Crash occurs here; Register read error
    while True:
        try:
            disconnected = not bno.begin()
        except Exception as e:
            print(e)
            time.sleep(0.1)
            failureCount += 1
            if failureCount > 10:
                print('You\'re a failure, just like this code')
                gyroRunning = False
        else:
            break

        if disconnected:
            print('Failed to initialize BNO055! Is the sensor connected?')
            gyroRunning = False

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

        MEASUREMENTS = 10

        for i in range(5):
            bno.read_euler()
            bno.read_linear_acceleration()
            time.sleep(0.1)

        global defaultRotation, defaultAcc
        defaultRotation = {'heading': 0, 'roll': 0, 'pitch': 0}
        defaultAcc = {'x': 0, 'y': 0, 'z': 0}
        # take ten measurements and average them
        for i in range(MEASUREMENTS):
            heading, roll, pitch = bno.read_euler()
            print(heading, roll, pitch, end=' ')
            defaultRotation['heading'] += heading
            defaultRotation['roll'] += roll
            defaultRotation['pitch'] += pitch

            x, y, z = bno.read_linear_acceleration()
            print(x, y, z)
            defaultAcc['x'] += x
            defaultAcc['y'] += y
            defaultAcc['z'] += z

            time.sleep(0.1)

        defaultRotation['heading'] /= MEASUREMENTS
        defaultRotation['roll'] /= MEASUREMENTS
        defaultRotation['pitch'] /= MEASUREMENTS

        defaultAcc['x'] /= MEASUREMENTS
        defaultAcc['y'] /= MEASUREMENTS
        defaultAcc['z'] /= MEASUREMENTS

        print(defaultAcc)
        print(defaultRotation)




# ------------------------
# ---- Main Function -----
# ------------------------

#time.sleep(abs(time.time() % -10)) # wait till the next whole 10 seconds
#starttime = time.time()

def getDataFragment():
    t = time.localtime()
    t = ':'.join([str(i).zfill(2) for i in [t.tm_hour, t.tm_min, t.tm_sec]])

    try:
        if TEMPSENSOR:
            externalTemp = round(tempSensor.getTemp(), 2)
        else:
            externalTemp = -1
    except:
        externalTemp = 'Error'

    try:
        coreTemp = os.popen('/opt/vc/bin/vcgencmd measure_temp').read()
        coreTemp = round(coreTemp[coreTemp.index('=')+1:-3], 2)
    except:
        coreTemp = 'Error'

    # Gyro Sensors
    try:
        heading, roll, pitch = bno.read_euler()

        heading -= defaultRotation['heading']
        roll -= defaultRotation['roll']
        pitch -= defaultRotation['pitch']

        heading = round(heading, 2)
        roll = round(roll, 2)
        pitch = round(pitch, 2)

        sys, gyro, accel, mag = bno.get_calibration_status()
        x, y, z = bno.read_magnetometer()
        magField = pow(x ** 2 + y ** 2 + z ** 2, 0.5)
        magField = round(magField / 100, 3) # 100 microTesla = 1 Gauss

        x, y, z = bno.read_linear_acceleration()

        x -= defaultAcc['x']
        y -= defaultAcc['y']
        z -= defaultAcc['z']

        x = round(x, 3)
        y = round(y, 3)
        z = round(z, 3)

        internalTemp = round(bno.read_temp(), 2)
    except:
        heading, roll, pitch = 'Error', 'Error', 'Error'
        magField = 'Error'
        x, y, z = 'Error', 'Error', 'Error'
        internalTemp = 'Error'
        gyroRunning = False

    if not gyroRunning:
        print('Attempting to restart gyro')

        gyroRunning = True
        setup()


    fragment = [t, externalTemp, coreTemp, internalTemp, \
                      heading, roll, pitch, \
                      magField, x, y, z]

    if not silent:
        print(fragment)

    #print(time.ctime())
    #time.sleep(pause - ((time.time() - starttime) % pause))

    return fragment
