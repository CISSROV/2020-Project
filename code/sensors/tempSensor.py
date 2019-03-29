#!/usr/bin/env python 

from os import system
system('sudo modprobe w1-gpio')
system('sudo modprobe w1-therm')

path = '/sys/bus/w1/devices'
idName = '28-0415a755f7ff'
file = 'w1_slave'

absPath = path + '/' + idName + '/' + file

def getTemp():
    f = open(absPath)
    raw = f.read()
    f.close()

    if 'YES' not in raw:
        return None

    tmp = raw.split('t=')[1]
    tmp = tmp[:tmp.find('\n')]

    floatStr = tmp[:2] + '.' + tmp[2:]

    return float(floatStr)

# use getTemp() to get the temperature
if __name__ == '__main__':
    print(getTemp())
