#!/usr/bin/env python3.4 
import tempSensor
import time
import json

# Fetch data every x seconds
pause = 10.0 # in seconds

fileName = '/var/www/html/data.json'

f = open(fileName,'w')
f.write('[]') # reset the data
f.close()

time.sleep(abs(time.time() % -10)) # wait till the next whole 10 seconds
starttime = time.time()

localCopy = []

while True:
    t = time.localtime()
    t = ':'.join([str(i).zfill(2) for i in [t.tm_hour, t.tm_min, t.tm_sec]])
    
    value = tempSensor.getTemp()

    localCopy.append([t, value])

    try:
        f = open(fileName,'w')
        json.dump(localCopy, f, indent=4)
        f.write('\n')
        f.close()
    except IOError as e:
        print(e)
    
    print(time.ctime())
    time.sleep(pause - ((time.time() - starttime) % pause))
