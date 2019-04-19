import sys
#import socket
#import select
#import pygame
import time

trimUp = {
    'left': 0.0,
    'right': 0.0
}


data = '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23'
#s.recv(4096)
if not data:
    print('\nDisconnected from chat server')
    sys.exit()
else:
    #print data
    # sys.stdout.write(data)
    datalist = [float(i) for i in data.split()]
    assert len(datalist) == 24

    axis = ['xLeft', 'yLeft', 'xRight', 'yRight', 'triggerRight', 'triggerLeft']
    buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

    joystick1 = dict(zip(axis + buttons, datalist[:12]))
    joystick2 = dict(zip(axis + buttons, datalist[12:]))

    #
    #       /a/    \b\
    #     /////    \\\\\
    #
    #
    #     \\\\\    /////
    #      \c\     /d/
    #
    # ______________a_b_c_d
    # Back          - - + +
    # Front         + + - -
    # Strafe Left   - + - +
    # Strafe Right  + - + -
    # Rotate Left   - + + -
    # Rotate Right  + - - +
    #

    yLeft = 50 * joystick1['yLeft']
    xLeft = 50 * joystick1['xLeft']
    xRight = 50 * joystick1['xRight']

    motor_a =  yLeft - xLeft - xRight

    motor_b =  yLeft + xLeft + xRight

    motor_c = -yLeft - xLeft + xRight

    motor_d = -yLeft + xLeft - xRight

    #mixing
    #m1 = 90+forwardval+strafeval+turnval
    #m2 = 90+forwardval-strafeval-turnval
    #m3 = 90-forwardval+strafeval
    #m4 = 90-forwardval-strafeval


    motor_up_left  = 1 * (90 + upval + trimUp['left'])
    motor_up_right = -1 * (90 + upval + trimUp['right'])

    '''
    move2(m2) #motor 1
    move3(m1) #motor 2
    move4(m3) #motor 3
    move5(m4) #motor 4
    move6(m6)
    move7(m7)
    '''







#print(str(m1) +' '+str(m2)+' '+str(m3)+' '+str(m4)+' '+str(m6)+' '+str(m7)+' '+str(m12)+' '+str(m10))

# print datalist
print('Trim: [{0}, {1}]'.format(trimUp['left'], trimUp['right']))
print(joystick1)
print(joystick2)
print('\033[2J', end='')

# else :
# user entered a message
# s.send(msg)
# sys.stdout.write (msg + '\n[Me]'); sys.stdout.flush()
