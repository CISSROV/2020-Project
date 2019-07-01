#!/usr/bin/env python3.4

from os import system

# init the w1 thing
system('sudo modprobe w1-gpio')
system('sudo modprobe w1-therm')

# path of w1 devices
path = '/sys/bus/w1/devices'

# id of the w1 temperature probe
idName = '28-0415a755f7ff'

# file containing the probe's data
file = 'w1_slave'

#
# in the w1 system, the data value of the probe is continously set 
# to be the content of the w1_slave file
#

# put the values together to get the absolute path of the file
absPath = path + '/' + idName + '/' + file

def getTemp():
    # returns the temperature when called

    # read the file
    f = open(absPath)
    raw = f.read()
    f.close()

    # correct data reports include the string 'YES' in them
    # return None if this is not the case, i.e. it failed
    if 'YES' not in raw:
        return None

    # extract the temperature value from the report
    tmp = raw.split('t=')[1]
    tmp = tmp[:tmp.find('\n')]

    floatStr = tmp[:2] + '.' + tmp[2:]

    return float(floatStr)

# use getTemp() to get the temperature
if __name__ == '__main__':
    print(getTemp())
