import RPi.GPIO as GPIO
import time
import socket
import json # useful methods: loads, dumps, JSONDecodeError

from sys import implementation, stderr, argv

#### Version: 1.1
#### Uses motorControlProtocol Version 1.0
#### if updates are made to this file or the protocol, please update version numbers

# <settings>
PORT = 5000
VERBOSE = False
# </settings>


#### ----  Dealing with command line arguments  ---- ####

if '--help' in argv:
    print('usage: python3.4 motorControlWithTCP.py [--help] [-p port] [--verbose]')
    exit(0)

if '--verbose' in argv:
    VERBOSE = True

for i in range(len(argv)):
    arg = argv[i]
    if arg.startswith('-p'):
        if i + 1 >= len(argv) or not argv[i + 1].isalnum():
            print('Incorrect usage of -p flag', file=stderr)
        else:
            PORT = int(argv[i + 1])
        break


#### ----  Dealing with obtaining the IP address on different platforms  ---- ####

platform = implementation._multiarch
if platform == 'arm-linux-gnueabihf':
    # on a raspberry pi
    from os import popen
    ip = popen("hostname -I").read().split()
    if len(ip) == 0:
        raise LookupError('No ip found')
    ip = ip[0]
elif platform == 'darwin':
    # on a mac
    ip = socket.gethostbyname(socket.gethostname())
else:
    raise Exception('Unknown platform')


#### ----  motor class  ---- ####
# contains info for one motor and a method to set the motor

class motor:

    def __init__(self, idname, IN1, IN2):
        # IN1 and IN2 are pin numbers
        self.idname = idname # must be unique!
        self.IN1 = IN1
        self.IN2 = IN2

        GPIO.setup(IN1,GPIO.OUT)
        GPIO.setup(IN2,GPIO.OUT)

        # start up
        GPIO.output(IN1, GPIO.LOW)
        self.p = GPIO.PWM(IN2, 50)
        self.p.start(0)

    def set(self, direction, power):
        # motor should be type RPi.GPIO.PWN
        # direction should be 'HIGH' or 'LOW'
        # power should be 0 <= power <= 100
        if direction not in [0, 1]:
            raise ValueError('direction arg is not norminal: Expectd 0 or 1, but got {0}'.format(direction))
        if power < 0 or power > 100:
            raise ValueError('power arg is not norminal: Expectd in range [0, 100], but got {0}'.format(direction))

        if direction == GPIO.HIGH:
            power = 100 - power

        GPIO.output(self.IN1, direction)
        self.p.ChangeDutyCycle(power)

    def cleanup(self):
        # call this when shutting down
        GPIO.output(self.IN1, GPIO.LOW)
        self.p.stop()


#### ----  masterMotorControl class  ---- ####
# contains a list of all motors and runs a socket server to receive commands to set motors

class masterMotorControl:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.motors = {}

        '''
        self.motors is in the format:
        {
            'idname1' : motorobject1,
            'idname2' : motorobject2,
            'idname3' : motorobject3,
            ...
        }
        '''

        self.sock = socket.socket()
        self.sock.bind((ip, PORT))
        print("Bound socket. IP: {0}, Port: {1}".format(ip, PORT))

        self.client = None

    def addMotor(self, motorObject):
        if not isinstance(motorObject, motor):
            raise TypeError('motorObject arg is not norminal: Expectd a motor object, but got {0}'.format(type(motorObject)))

        self.motors[motorObject.idname] = motorObject
        print('Added motor with idname {0}'.format(motorObject.idname))

    def run(self):
        try:
            self._run()
        finally:
            print('Shutting Down')
            self.cleanup()

    def _run(self):
        self.sock.listen(1)
        print('Waiting for connection (soon)')
        self.client, info = self.sock.accept()
        print('Client info:', *info)
        
        # 1st line
        self.client.send(b'HELLO CLIENT\n')

        # 2nd line
        msg = b'HELLO SERVER\n'
        data = self.client.recv(len(msg))
        if msg != data:
            raise ValueError('Did not receive proper answer, instead got this: {0}'.format(data.decode()))
        self.client.send(b'Motor names\n')

        # 3rd line
        tmp = json.dumps(list(self.motors.keys()))
        self.client.send(tmp.encode())

        # 4th line
        msg = b'OK\n'
        data = self.client.recv(len(msg))
        if msg != data:
            raise ValueError('Did not receive proper answer, instead got this: {0}'.format(data.decode()))

        del data, msg, tmp
        


        # main communication
        buffer1 = b''
        while (True):
            tmp = self.client.recv(128) # why 128? cause i felt like it
            if tmp == b'':
                # connection closed by peer
                return

            buffer1 += tmp
            tmp = buffer1.split(b'\n')
            buffer1 = tmp[-1]
            tasks = tmp[:-1]

            for task in tasks:
                try:
                    task = json.loads(task.decode())
                except json.JSONDecodeError as e:
                    print('Not norminal:', e, file=stderr)
                    continue

                for idname in task: # task is a dict (hopefully)
                    if idname not in self.motors:
                        print('Not norminal idname, got {0}'.format(idname), file=stderr)
                    else:
                        self.motors[idname].set(*task[idname])
                        # '*' unpacks the list of two items and passes them as two arguments to .set()
                        if VERBOSE:
                            print('Completed task: {0}'.format(task[idname]))

    def cleanup(self):
        # call this after _run() to clean up
        try:
            for idname in self.motors:
                self.motors[idname].cleanup()
        finally:
            GPIO.cleanup()
            self.sock.close()
            if (self.client):
                self.client.close()


#### ----  start of program  ---- ####

if __name__ == '__main__':
    master = masterMotorControl()

    master.addMotor(motor('test1', 21, 20)) # for testing. alter + copy line for each attached motor

    master.run()
