'''
The CISSROV Code module.
All python code for CISSROV is found here, divied up into 4 groups.

cgi-bin holds scripts that can be run remotely
using the Apache server on surface pi.

core holds the code for controlling the motors
of the ROV and the communication required between
the pis to make it happen

mini-rov is like core, but for the mini rov
that was part of the 2019 MATE Competition.
It likely has no more use.

sensors contains code for collecting sensor
data from the ROV, like the gyroscope and
thermometer, and then sending it on
to webpages that connect to the sensor
websocket server with javascript.

The code heavily relies on the
libraries `autobahn` and `twisted`
for websocket communication.
Except for cgi-bin, all
communication happens with websockets.
The libaries have to be installed on surface pi
and motor pi.

The python version used for all code is python3.4, because
it was the newest version on the raspberry pis used.

Author: Jonathan Rotter except when specified otherwise.
Then it is Danny or Yilou's code.
'''

import sys
sys.path.append(sys.path[0] + '/code/core')
sys.path.append(sys.path[0] + '/code/mini-rov')
sys.path.append(sys.path[0] + '/code/cgi-bin')
sys.path.append(sys.path[0] + '/code/sensors')
