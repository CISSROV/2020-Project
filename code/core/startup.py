#!/usr/bin/env python3

import os
import sys

def runShellCmd(cmd):
    f = os.popen(cmd)
    txt = f.read()
    f.close()
    return txt

baseCmd = 'sshpass -p raspberry ssh pi@192.168.1.3 sudo /var/www/scripts/dataCollection.sh'

if len(sys.argv) <= 1:
    # no argument supplied
    print('Usage: startup.py [start|stop]')
    sys.exit(1)

if sys.argv[1] in ['start', 'stop']:
    # run cmd and pass the argument along
    txt = runShellCmd(baseCmd + ' ' + sys.argv[1])
    print(txt)

else:
    # unknown argument supplied
    print('Usage: startup.py [start|stop]')
    sys.exit(1)

sys.exit(0)