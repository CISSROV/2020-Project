#!/usr/bin/env python3.4
'''
Author: Jonathan Rotter

Accesses the other log file that
is used by `server2020.py`.
Crashes that happen before it
has fully started end up in the
log file read by this program,
while crashes that happen while
the program is running end up in
the other logfile. `getLog.py`
reads that logfile.
'''

# Print header specifying file type
print("Content-type: text/html\n\n")

try:
    # Open and read the other websocket log file
    f = open('/var/www/scripts/nohup.out', 'r')
    raw = f.read()
    f.close()

    # Replace the char '\n' with html's line break <br>
    raw = raw.replace('\n', '<br>')

    # Send file contents to sys.stdout
    # which sends it to be displayed on the webpage
    print(raw)
except FileNotFoundError as e:
    # Error Reporting
    print(e)
