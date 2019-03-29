#!/usr/bin/env python3.4

from sys import path
path.append('/var/www/scripts')
import tempSensor

print ("Content-type: text/html\n\n")

f = open('temperature.html')
txt = f.read()
f.close()

data = tempSensor.getTemp()

txt = txt.replace('<!-- tag -->', str(data))

print(txt)
