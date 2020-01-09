#!/usr/bin/env python3.4

'''Author: Jonathan Rotter

Server code

To be run on server pi. It is required (probably) that
it is started before motor2020++.py or surface2020.py

Once it is running it does not need to be restarted
even if its clients restart or lose connection

Required 3rd-party libraries:
`autobahn`
`twisted`
'''

# Check if the version of python is 3.x
import sys
if sys.version[0] != '3':
    # Stop running if the version is python 2.x
    raise Exception('This is Python3 code')

# importing the necessary objects
# autobahn does websocket stuff, but relies on twisted
from autobahn.twisted.websocket import \
    WebSocketServerProtocol, WebSocketServerFactory

# twisted does asynchronous code execution needed for websockets
from twisted.python import log
from twisted.internet import task, reactor

IP = '127.0.0.1'
'''ip is localhost, does not need to be changed'''

PORT = 8008
'''Make sure the port set here and in webSocketClient are the same'''


class ServerProtocol(WebSocketServerProtocol):
    '''
    Describes how the websocket server should act
    with one connection

    How to connect to it in JavaScript
    ws = new WebSocket('ws://localhost:8008/motor')
    ws = new WebSocket('ws://localhost:8008/surface')
    '''

    def onConnect(self, request):
        '''
        Called by the server factory when
        a client connects.
        The path is found in `request.path`
        and is used for the clients to specify
        whether they are motor2020 or surface2020
        '''

        print(request.path)
        # debug information
        print('Client connecting & registering: {0}'.format(request.peer))
        clientTypeRequest = request.path

        # process the type of request
        if clientTypeRequest.startswith('/'):
            # remove the slash if there is one
            clientTypeRequest = clientTypeRequest[1:]

        # tell the factory to remember the connection
        self.factory.register(self, clientTypeRequest)

    def onOpen(self):
        '''
        Called by the server factory.
        Only prints debug info
        '''
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        '''
        Called by the server factory when
        a client disconnects
        '''
        print('WebSocket connection closed & deregistering: {0}'.format(reason))

        # tell the factory that this connection is dead
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        '''
        Called by the server factory when
        the client send a message.
        The message is then sent to all
        other connected clients
        '''

        # tell the factory to broadcast the received message
        # to all other connected clients
        self.factory.broadcast(self, msg, isBinary)


class ServerFactory(WebSocketServerFactory):
    '''
    Keeps track of all connections and relays data to other clients
    '''

    def __init__(self, url):
        '''
        Initializes the class

        Args:
            url (str): has to be in the format of "ws://127.0.0.1:8008"
        '''
        WebSocketServerFactory.__init__(self, url)

        # init fields
        self.motorConnection = None
        self.miniMotorConnection = None
        self.surfaceConnection = None

    def register(self, client, clientTypeRequest):
        '''
        Called in `ServerProtocol.onConnect`
        Remembers a connecting client so that
        later data can be received from or broadcast to the client

        Args:
            client (ServerProtocol): A instance representing the connection
            clientTypeRequest (str): Whether the client is surface or motor pi
        '''

        if clientTypeRequest == 'surface':
            self.surfaceConnection = client  # surface sends joystick data

        elif clientTypeRequest == 'motor':
            self.motorConnection = client  # motor receives joystick data

        elif clientTypeRequest == 'miniROV':
            self.miniMotorConnection = client  # mini-rov recives joystick data

        else:
            print('Bad client type received: {}'.format(clientTypeRequest))
            # end the connection because the client's type is not recognized
            # the type the client is is specified by the path in the url
            client._closeConnection()
            # find some better way to end the connection; unclean closing

    def unregister(self, client):
        '''
        Called in `ServerProtocol.onClose`
        Removes a client from the list of clients
        as it is disconnecting from the server

        Args:
            client (ServerProtocol): The connection to remove
        '''

        if self.surfaceConnection == client:
            self.surfaceConnection = None

        elif self.motorConnection == client:
            self.motorConnection = None

        elif self.miniMotorConnection == client:
            self.miniMotorConnection = None

        else:
            print('Unknown client: {}'.format(client))

    def broadcast(self, client, msg, isBinary):
        '''
        Broadcasts data to other connections.
        This is how surface pi sends the
        state of the XBox controller to motor pi

        Arg:
            client (ServerProtocol): The source of the message
            msg (str or bytes): The message to relay
            isBinary (bool): If the msg is already encoded
        '''

        # only surface pi is supposed to send data
        if self.surfaceConnection == client:

            # broadcast to motor2020
            if self.motorConnection:
                self.motorConnection.sendMessage(msg)

            # broadcast to miniROV
            if self.miniMotorConnection:
                self.miniMotorConnection.sendMessage(msg)

        # debug messages
        elif self.motorConnection == client:
            print('Motor Pi isn\'t supposed to send stuff')

        elif self.miniMotorConnection == client:
            print('Mini ROV isn\'t supposed to send stuff')


if __name__ == '__main__':
    # display debug information to stdout for now
    log.startLogging(sys.stdout)  # TODO: replace with log file (maybe)

    # Setup server factory
    server = ServerFactory(u'ws://{}:{}'.format(IP, PORT))
    server.protocol = ServerProtocol

    # setup listening server
    reactor.listenTCP(PORT, server)

    try:
        # start listening for and handling connections
        reactor.run()
    finally:
        pass
        # if logs are sent to a file instead of stdout
        # the file should be closed here with f.close()
