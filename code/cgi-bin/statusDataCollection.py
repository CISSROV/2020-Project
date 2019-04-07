#!/usr/bin/env python3.4
import os

print ("Content-type: text/html\n\n")

f = os.popen('pgrep -f "sudo python3.4 data"')
result = f.read()
f.close()
if result.strip() == '':
    result = 'None'
result = result.split()[0]

print('<h3>dataCollection Status</h3>')
print('<p id="PID">PID: ' + str(result) + '</p>')
