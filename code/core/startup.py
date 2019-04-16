#!/usr/bin/env python3

import os
import sys

def runShellCmd(cmd):
    f = os.popen(cmd)
    txt = f.read()
    f.close()
    return txt

baseCmd = 'sshpass -p raspberry ssh pi@192.168.1.3'
script = 'sudo /var/www/scripts/dataCollection.sh'

if len(sys.argv) <= 1:
    # no argument supplied
    print('Usage: startup.py [start|stop|check]')
    sys.exit(1)

if sys.argv[1] in ['start', 'stop']:
    # run cmd and pass the argument along
    txt = runShellCmd(' '.join([baseCmd, script, sys.argv[1]]))
    print(txt)

    if sys.argv[1] == 'start':
        print('\n')
        print('Use "startup.py stop" to stop the program on camera pi')

elif sys.argv[1] == 'check':
    print('Check')
    check = 'pgrep -f "sudo python3.4 data"'
    txt = runShellCmd(' '.join([baseCmd, check]))
    print(txt)

else:
    # unknown argument supplied
    print('Usage: startup.py [start|stop|check]')
    sys.exit(1)

sys.exit(0)