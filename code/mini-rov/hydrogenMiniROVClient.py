#!/usr/bin/env python
import motorInterface
import sys
import socket
import select
import time

# these are in a row

# this motor is IN3/4 on the edge of the motor controller
m1 = motorInterface.motor(16, 26)
# next to the one above
m2 = motorInterface.motor(12, 13)

# 2nd chip
m3 = motorInterface.motor(27, 23)
m4 = motorInterface.motor(4, 18)

def move1(pow):
    m1.set(pow)

def move2(pow):
    m2.set(pow)

def move3(pow):
    m3.set(pow)

def move4(pow):
    m4.set(pow)


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
    if num == 2:
        if button == 'LB':
            trimUp['left'] += 1
            trimUp['right'] += 1
        elif button == 'RB':
            trimUp['left'] -= 1
            trimUp['right'] -= 1

########Multiple clients connect to a server than send and receive data to all clients
def chat_client(host='192.168.1.2', port=9009):
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
                    datalist = [float(i) for i in data.split()[2:]]

                    for i in range(len(datalist)):
                        if abs(datalist[i]) < 0.1:
                            datalist[i] = 0.0

                    assert len(datalist) == 24

                    axis = ['xLeft', 'yLeft', 'triggerLeft', 'xRight', 'yRight', 'triggerRight']
                    buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB']

                    joystick1 = dict(zip(axis + buttons, datalist[:12]))
                    joystick2 = dict(zip(axis + buttons, datalist[12:]))

                    global justPressed1, justPressed2

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

                    # motors go from -100 to 100

                    yLeft = 50 * joystick2['yLeft']
                    xLeft = 50 * joystick2['xLeft']
                    yRight = 50 * joystick2['yRight']
                    xRight = 50 * joystick2['xRight']

                    spin = 0

                    joystick2['triggerRight'] = (joystick2['triggerRight'] + 1) / 2

                    joystick2['triggerLeft'] = (joystick2['triggerLeft'] + 1) / 2

                    if joystick2['triggerRight'] >= 0.1 and joystick2['triggerLeft'] >= 0.1:
                        pass # do nothing cause both are pressed
                    else:
                        if joystick2['triggerRight'] > 0.1:
                            # spin right
                            spin = joystick2['triggerRight'] * 60

                        if joystick2['triggerLeft'] > 0.1:
                            # spin left
                            spin = -joystick2['triggerLeft'] * 60


                    motor_a = yLeft - xLeft - spin

                    motor_b = yLeft + xLeft + spin

                    motor_c = -yLeft + xLeft - spin

                    motor_d = -yLeft - xLeft + spin

                    #mixing
                    #m1 = 90+forwardval+strafeval+turnval
                    #m2 = 90+forwardval-strafeval-turnval
                    #m3 = 90-forwardval+strafeval
                    #m4 = 90-forwardval-strafeval

                    global trimUp

                    motor_up_left  = trimUp['left'] + yRight
                    motor_up_right = trimUp['right'] + yRight

                    def bounds(x):
                        # max power is -100 to 100
                        if x < -50:
                            return -50
                        if x > 50:
                            return 50
                        return x

                    motor_a = bounds(motor_a)
                    motor_b = bounds(motor_b)
                    motor_c = bounds(motor_c)
                    motor_d = bounds(motor_d)

                    # --------------- FIX THIS MOTOR STUFF ---------------

                    motor_up_left  = bounds(motor_up_left)
                    motor_up_right = bounds(motor_up_right)


                    # right

                    move4(motor_a)
                    move2(motor_b)
                    move3(motor_c)
                    move5(motor_d)

                    # 150 down up, 30 move up
                    move6(motor_up_right) # stop on 93
                    move7(motor_up_left) # stop on 93

                    move8(motor_claw)








                #print(str(m1) +' '+str(m2)+' '+str(m3)+' '+str(m4)+' '+str(m6)+' '+str(m7)+' '+str(m12)+' '+str(m10))

                # print datalist
                for i in range(30):
                    print '\r\033[A\033[K',

                print('Trim: [{0}, {1}]'.format(trimUp['left'], trimUp['right']))
                print(joystick1)
                print(joystick2)
                print(motor_a, motor_b)
                print(motor_c, motor_d)
                print ''
                print(motor_up_left, motor_up_right)
                print(motor_claw)


                # else:
                # user entered a message
                # s.send(msg)
                # sys.stdout.write (msg + '\n[Me]'); sys.stdout.flush()

if __name__ == "__main__":
    try:
        chat_client()
    finally:
        print('Done')
        motorInterface.cleanup()
    
    
