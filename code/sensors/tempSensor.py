#!/usr/bin/env python3.4
'''
Author: Jonathan Rotter

Code for collecting data from
the external temperature sensor.

This process may have to be run
as root (with sudo) because it makes
use of sudo
'''

from os import system

if __name__ == "__main__":
    # init the w1 thing
    system('sudo modprobe w1-gpio')
    system('sudo modprobe w1-therm')

path = '/sys/bus/w1/devices'
'''Path to w1 devices'''

idName = '28-0415a755f7ff'
'''id of the w1 temperature probe'''

file = 'w1_slave'
'''
File containing the probe's data.
in the w1 system, the data value of the probe is continuously
set to be the content of the w1_slave file
'''

absPath = path + '/' + idName + '/' + file
'''
Absolute path to the `file`, put together from `path`, `id`, and `file`
'''


def getTemp():
    '''
    Gets the temperature

    Return:
        temp: The temperature as a float in Celsius
    '''

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
