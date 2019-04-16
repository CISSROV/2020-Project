#!/usr/bin/env python3.4 
import tempSensor
import time
import json
import os

# ----------------------------------------------------
# ---- Deprecated - Refer to dataCollectShards.py ----
# ----------------------------------------------------

# fix sys.path
import sys
sys.path.append('/home/pi/Adafruit_Python_BNO055')
from Adafruit_BNO055 import BNO055

# args for displaying debug info
silent = True
if len(sys.argv) >= 2:
    if (sys.argv[1] == '-v'):
        silent = False

# Fetch data every x seconds
pause = 5 # in seconds

# ---------------------------
# ---- Gyro Startup Code ----
# ---------------------------

bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

# ---------------------------
# ---- JSON & Main Loop -----
# ---------------------------

fileName = '/var/www/html/data.json'

f = open(fileName,'w')
f.write('[]') # reset the data
f.close()

time.sleep(abs(time.time() % -5)) # wait till the next whole 5 seconds
starttime = time.time()

localCopy = [] # contains data of this session

while True:
    t = time.localtime()
    t = ':'.join([str(i).zfill(2) for i in [t.tm_hour, t.tm_min, t.tm_sec]]) # time in hh:mm:ss
    
    externalTemp = tempSensor.getTemp() # (water) temperature probe
    
    coreTemp = os.popen('/opt/vc/bin/vcgencmd measure_temp').read()
    coreTemp = coreTemp[coreTemp.index('=')+1:-3] # raspberry pi core temperature
    
    # Gyro Sensors

    heading, roll, pitch = bno.read_euler() # direction
    sys, gyro, accel, mag = bno.get_calibration_status() # idk why this
    x, y, z = bno.read_magnetometer() # magnetic field
    magField = pow(x ** 2 + y ** 2 + z ** 2, 0.5) # absolute value
    magField = magField / 100 # 100 microTesla = 1 Gauss
    
    x, y, z = bno.read_linear_acceleration() # without gravity

    internalTemp = bno.read_temp() # gyroscope's temperature probe

    localCopy.append([t, externalTemp, coreTemp, round(internalTemp, 2), \
                      round(heading, 2), round(roll, 2), round(pitch, 2), \
                      round(magField, 4), round(x, 3), round(y, 3), round(z, 3)])

    if not silent:
        print(localCopy[-1])
    try:
        # write to file
        f = open(fileName,'w')
        json.dump(localCopy, f, indent=4)
        f.write('\n')
        f.close()
    except IOError as e:
        print(e)
    
    # wait pause number of seconds minus the time the code took to run
    print(time.ctime())
    time.sleep(pause - ((time.time() - starttime) % pause))
