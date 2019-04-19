import sys
import socket
import select
import pygame
import time

trimUp = {
    'left': 0.0,
    'right': 0.0
}

data = ''
#s.recv(4096)
if not data:
    print('\nDisconnected from chat server')
    sys.exit()
else:
    #print data
    # sys.stdout.write(data)
    datalist = data.split()

    forwardval = int(float(datalist[3]))*45
    if abs(float(datalist[2])) > 0.1:
        strafeval = int(float(datalist[2]))*20
    else:
        strafeval = 0

    if abs(float(datalist[5])) > 0.1:
        turnval = int(float(datalist[5]))*20
    else:
        turnval = 0

    if abs(float(datalist[6])) > 0.1:
        upval = int(float(datalist[6]))*40
    else:
        upval = 0

    if abs(float(datalist[6])) > 0.1:
        tiltval = 0
    else:
        tiltval = 0
    #mixing
    m1 = 90+forwardval+strafeval+turnval
    m2 = 90+forwardval-strafeval-turnval
    m3 = 90-forwardval+strafeval
    m4 = 90-forwardval-strafeval

    m_up_left  = 97 + upval + tiltval + trimUp['left']
    m_up_right = 97 - upval - tiltval + trimUp['right']

    '''
    move2(m2) #motor 1
    move3(m1) #motor 2
    move4(m3) #motor 3
    move5(m4) #motor 4
    move6(m6)
    move7(m7)
    '''







print(str(m1) +' '+str(m2)+' '+str(m3)+' '+str(m4)+' '+str(m6)+' '+str(m7)+' '+str(m12)+' '+str(m10))

# print datalist
sys.stdout.write('[Me] '); sys.stdout.flush()

# else :
# user entered a message
# s.send(msg)
# sys.stdout.write (msg + '\n[Me]'); sys.stdout.flush()
