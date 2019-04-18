import sys
import socket
import select
import pygame
import time

port = '/dev/ttyACM0'

import pyfirmata

########Below is superfluous code necessary only for receiving and sending controller input
# pygame.init()
# joystick = pygame.joystick.Joystick(0)
# joystick.init()


# def print_data():
#   data = joystick.get_axis(0)
#   data2 = joystick.get_axis(1)
#   data3 = joystick.get_axis(2)
#   data4 = joystick.get_axis(3)    
#   data5 = joystick.get_axis(4)
#   data6 = joystick.get_axis(5)
#   data = round(data, 2)
#   data2 = round(data2, 2)
#   data3 = round(data3, 2)
#   data4 = round(data4, 2)
#   data5 = round(data5, 2)
#   data6 = round(data6, 2)
#   mesg = str(data) + " " + str(data2) + " " + str(data3) + " " + str(data4) + " " + str(data5) + " " + str(data6)
#   # print msg
#   pygame.event.pump()
#   time.sleep(0.05)
        
#   return mesg
        


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


########Multiple clients connect to a server than send and receive data to all clients
def chat_client(host=None, port=None):
    m10 = 90
    m12 = 0
    global buffer
    if (host == None or port == None):
        if(len(sys.argv) < 3) :
            print 'Usage : python chat_client.py 192.168.1.__ 9009'
            sys.exit()

        host = sys.argv[1]
        port = int(sys.argv[2])    

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'Connected to remote host. You can start sending messages'
    sys.stdout.write('[Me] '); sys.stdout.flush()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])

        for sock in ready_to_read:
        # print ("sock " +str(sock))
        #print ("s "+str(s))
             
            if sock == sock:
        
                # incoming message from remote server, s
                data = s.recv(4096)
                if not data:
                    print '\nDisconnected from chat server'
                    sys.exit()
                else:
                    #print data
                    # sys.stdout.write(data)
                    datalist = data.split()
                    
                    forwardval = int(float(datalist[3]))*45
                    if abs(float(datalist[3])) > 0.1: 
                        strafeval = int(float(datalist[2]))*20
                    else:
                        strafeval = 0
                        
                    if abs(float(datalist[2])) > 0.1:
                        turnval = int(float(datalist[5]))*20
                    else:
                        turnval = 0
                    
                    if abs(float(datalist[5])) > 0.1:
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
                    m7 = 97+upval+tiltval
                    m6 = 97-upval-tiltval
            
                    move2(m2) #motor 1
                    move3(m1) #motor 2
                    move4(m3) #motor 3
                    move5(m4) #motor 4
                    move6(m6)
                    move7(m7)
            
            
                    




            print str(m1) +' '+str(m2)+' '+str(m3)+' '+str(m4)+' '+str(m6)+' '+str(m7)+' '+str(m12)+' '+str(m10)
                    
                    # print datalist
                    sys.stdout.write('[Me] '); sys.stdout.flush()     
            
           # else :
                # user entered a message
               # s.send(msg)
               # sys.stdout.write (msg + '\n[Me]'); sys.stdout.flush() 
                






if __name__ == "__main__":

    sys.exit(chat_client())

def run(host, port):        # added by jrotter
    chat_client(host, port)


