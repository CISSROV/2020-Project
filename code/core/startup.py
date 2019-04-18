#!/usr/bin/env python3

# 
# May or may not work.
# Low priority program,
# mostly just for convenience
# 

import sys
import fcntl
import time
from os import O_NONBLOCK
import subprocess

pseudo = False

def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | O_NONBLOCK)
    try:
        return output.read()
    except:
        return ""

def runShellCmd(cmd, idk=False):
    pre = 'bash -c "{0}"'

    global pseudo
    if pseudo:
        print(pre.format(cmd))
        sys.exit(0)

    f = subprocess.Popen(pre.format(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if idk == 'start':
        while True:
            try:
                a = non_block_read(f.stdout)
                if a != b'' and a != None:
                    print(a.decode(), end='')
                else:
                    pass
            except Exception as e:
                print('Error:', e)
                break
            time.sleep(0.1)
    else:
        try:
            raw = f.communicate()
            txt = '\n\n'.join([i.decode() for i in raw if i.strip() != b''])
            return txt
        except Exception as e:
            raise
        else:
            pass
        finally:
            return ''
    
    f.stdout.close()
    f.stderr.close()
    
    return ''
    
baseCmd = 'sshpass -p raspberry ssh pi@192.168.1.3'
script = 'sudo /var/www/scripts/dataCollection.sh'

if len(sys.argv) <= 1:
    # no argument supplied
    print('Usage: startup.py [start|stop|check]')
    sys.exit(1)

if len(sys.argv) >= 3:
    if sys.argv[2] == '--debug':
        pseudo = True

if sys.argv[1] in ['start', 'stop']:
    # run cmd and pass the argument along
    txt = runShellCmd(' '.join([baseCmd, script, sys.argv[1]]), sys.argv[1])
    print(txt)

    if sys.argv[1] == 'start':
        print('\n')
        print('Use "startup.py stop" to stop the program on camera pi')

elif sys.argv[1] == 'check':
    print('Check')
    check = 'pgrep -f \"sudo python3.4 data\"'
    txt = runShellCmd(' '.join([baseCmd, check]))
    print(txt)

else:
    # unknown argument supplied
    print('Usage: startup.py [start|stop|check]')
    sys.exit(1)

sys.exit(0)