import sys
import socket
import select
import pygame
import time
'''
port = '/dev/ttyACM0'

import pyfirmata

#setup pyFirmata
board =  pyfirmata.Arduino(port)

#setup an iterator for safety
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

#locate pins
pin2 = board.get_pin('d:2:s') #motor 1
pin3 = board.get_pin('d:3:s') #motor 1
pin4 = board.get_pin('d:4:s') #motor 2
pin5 = board.get_pin('d:5:s') #motor 3
pin6 = board.get_pin('d:6:s') #motor 3
pin7 = board.get_pin('d:7:s') #motor 3
pin8 = board.get_pin('d:8:s') #motor 3
pin9 = board.get_pin('d:9:s') #motor 3
pin10 = board.get_pin('d:10:s') #motor 3
pin12 = board.get_pin('d:12:s') #motor 3

def move2(a):
    pin2.write(a)

def move3(a):
    pin3.write(a)

def move4(a):
    pin4.write(a)

def move5(a):
    pin5.write(a)

def move6(a):
    pin6.write(a)

def move7(a):
    pin7.write(a)

def move8(a):
    pin8.write(a)

def move9(a):
    pin9.write(a)

def move10(a):
    pin10.write(a)

def move12(a):
    pin12.write(a)
'''
trimUp = {
    'left': 0.0,
    'right': 0.0
}

justPressed1 = {
    'A': False,
    'B': False,
    'X': False,
    'Y': False,
    'LB': False,
    'RB': False
}

justPressed2 = {
    'A': False,
    'B': False,
    'X': False,
    'Y': False,
    'LB': False,
    'RB': False
}

def buttonPressed(button, num):
    global trimUp
    if num == 1:
        if button == 'LB':
            trimUp['left'] += 1
            trimUp['right'] += 1
        elif button == 'RB':
            trimUp['left'] -= 1
            trimUp['right'] -= 1

########Multiple clients connect to a server than send and receive data to all clients
def chat_client(host=None, port=None):
    m10 = 90
    m12 = 0
    global buffer
    if (host == None or port == None):
        if(len(sys.argv) < 3):
            print('Usage: python chat_client.py 192.168.1.__ 9009')
            sys.exit()

        host = sys.argv[1]
        port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try:
        s.connect((host, port))
    except:
        print('Unable to connect')
        sys.exit()

    print('Connected to remote host. You can start sending messages')
    sys.stdout.write('[Me] '); sys.stdout.flush()

    while True:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])

        for sock in ready_to_read:
        # print ("sock " +str(sock))
        #print ("s "+str(s))

            if sock == sock:
                data = s.recv(4096)
                print(data)
                if not data:
                    print('\nDisconnected from chat server')
                    sys.exit()
                else:
                    #print data
                    # sys.stdout.write(data)
                    datalist = [float(i) for i in data.split()]

                    for i in range(len(datalist)):
                        if abs(datalist[i]) < 0.1:
                            datalist[i] = 0.0

                    assert len(datalist) == 24

                    axis = ['xLeft', 'yLeft', 'xRight', 'yRight', 'triggerRight', 'triggerLeft']
                    buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

                    joystick1 = dict(zip(axis + buttons, datalist[:12]))
                    joystick2 = dict(zip(axis + buttons, datalist[12:]))

                    for k in joystick1:
                        if k not in buttons:
                            continue
                        v = joystick1[k]
                        if v == 1 and not justPressed1[k]:
                            # just pressed
                            buttonPressed(k, 1)
                            justPressed1[k] = True
                        elif v == 0 and justPressed1[k]:
                            # just released
                            justPressed1[k] = False
                        elif v not in [1, 0]:
                            raise ValueError('Got {0}, expected 0 or 1'.format(v))
                        else:
                            pass

                    for k in joystick2:
                        if k not in buttons:
                            continue
                        v = joystick2[k]
                        if v == 1 and not justPressed2[k]:
                            # just pressed
                            buttonPressed(k, 2)
                            justPressed2[k] = True
                        elif v == 0 and justPressed2[k]:
                            # just released
                            justPressed2[k] = False
                        elif v not in [1, 0]:
                            raise ValueError('Got {0}, expected 0 or 1'.format(v))
                        else:
                            pass


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

                    if joystick1['triggerRight'] >= 0.1 and joystick1['triggerLeft'] >= 0.1:
                        pass # do nothing cause both are pressed
                    else:
                        if joystick1['triggerRight'] > 0.1:
                            upval = joystick1['triggerRight']

                        if joystick1['triggerLeft'] > 0.1:
                            upval = -joystick1['triggerLeft']


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
                print '\033[2J',
                print('Trim: [{0}, {1}]'.format(trimUp['left'], trimUp['right']))
                print(joystick1)
                print(joystick2)
                print(motor_a, motor_b)
                print(motor_c, motor_d)
                print(motor_up_left, motor_up_right)


                # else:
                # user entered a message
                # s.send(msg)
                # sys.stdout.write (msg + '\n[Me]'); sys.stdout.flush()

if __name__ == "__main__":
    chat_client()
    print('Done')
