#!/usr/bin/env python3.4
# Author: Jonathan Rotter
import os

# Print header specifying file type
print ("Content-type: text/html\n\n")

# Search for a process name beginning with "sudo python3.4 data"
# Runs it in a subshell and returns the result
f = os.popen('pgrep -f "sudo python3.4 data"')
result = f.read()
f.close()

# Analyze output from pgrep command
if result.strip() == '':
    result = 'None' # No process found
result = result.split() # ?
if len(result) == 1:
    result = 'None' # No process found
else:
    result = result[0]

# Print report in html
print('<h3>dataCollection Status</h3>')
print('<p id="PID">PID: ' + str(result) + '</p>')
