import socket
import json

#
# clientSideTest can be used to test the functionality of server side code
# and can send manual instructions to set the motors that the server side control
#

def main():
    ip =  '172.18.232.170'
    #ip = input('IP: ')
    port = 5000

    s = socket.socket()
    s.connect((ip,port))

    print('Connected')

    msg = b'HELLO CLIENT\n'
    data = s.recv(len(msg))
    if msg != data:
        raise ValueError('Did not receive proper answer, instead got this: {0}'.format(data.decode()))

    s.send(b'HELLO SERVER\n')

    print('Handshake complete')

    msg = b'Motor names\n'
    data = s.recv(len(msg))
    if msg != data:
        raise ValueError('Did not receive proper answer, instead got this: {0}'.format(data.decode()))

    buffer1 = b''
    while True:
        char = s.recv(1)
        if char == b'\n':
            break

        buffer1 += char

    ls = json.loads(buffer1.decode())

    print(ls)

    s.send(b'OK\n')

    name = ls[0]
    while True:
        direction = input('Direction (1|0)) ')
        power = input('Power (0-100)) ')

        data = {name: [direction,power]}
        print(data)
        data = json.dumps(data)        
        s.send(data.encode())
        s.send(b'\n')

if __name__ == '__main__':
    main()
