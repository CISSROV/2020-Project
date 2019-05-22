#!/usr/bin/env python3.4
# Author: Jonathan Rotter
import time

#
# Fetches today's websocket log
# For debugging purposes
# Access using /cgi-bin/getLog.py
#

def getDateISO8601():
    #
    # Gets the current local time and returns in the format YYYY-MM-DD
    #
    tmp = time.localtime()
    return '{}-{:0>2}-{:0>2}'.format(tmp.tm_year, tmp.tm_mon, tmp.tm_mday)

# Print header specifying file type
print("Content-type: text/html\n\n")

date = getDateISO8601()
try:
    # Open and read websocket log file
    f = open('/var/log/MATE/websocket{}.log'.format(date), 'r')
    raw = f.read()
    f.close()

    # Replace the char '\n' with html's line break <br>
    raw = raw.replace('\n', '<br>')

    # Send file contents to sys.stdout which sends it to be displayed on the webpage
    print(raw)
except FileNotFoundError as e:
    # Error Reporting
    print(e)
