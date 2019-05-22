#!/usr/bin/env python3.4
# Author: Jonathan Rotter

# Check if the version of python is 3.x
import sys
if sys.version[0] != '3':
    # Stop running if the version is python 2.x 
    raise Exception('This is Python3 code')

from autobahn.twisted.websocket import \
    WebSocketServerProtocol, WebSocketServerFactory

from twisted.python import log
from twisted.internet import task, reactor

# ip is localhost
IP = '127.0.0.1'
PORT = 8008

class ServerProtocol(WebSocketServerProtocol):
    #
    # Describes how the websocket server should act
    # with one connection
    #

    # How to connect to it in js
    # ws = new WebSocket('ws://localhost:8008/motor')
    # ws = new WebSocket('ws://localhost:8008/surface')

    def onConnect(self, request):
        # called by the server factory
        print(request.path)
        print('Client connecting & registering: {0}'.format(request.peer))
        clientTypeRequest = request.path

        # process the type of request
        if clientTypeRequest.startswith('/'):
            clientTypeRequest = clientTypeRequest[1:]

        # tell the factory to remember the connection
        self.factory.register(self, clientTypeRequest)

    def onOpen(self):
        # called by the server factory
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        # called by the server factory
        print('WebSocket connection closed & unregistering: {0}'.format(reason))

        # tell the factory that this connection is dead
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        # called by the server factory

        # tell the factory to broadcast the message to all other connected clients
        self.factory.broadcast(self, msg, isBinary)

class ServerFactory(WebSocketServerFactory):
    #
    # Keeps track of connection and relays data to other clients
    #

    def __init__(self, url):
        # url has to be in the format of "ws://127.0.0.1:8008"
        WebSocketServerFactory.__init__(self, url)

        self.motorConnection = None
        self.miniMotorConnection = None
        self.surfaceConnection = None

    def register(self, client, clientTypeRequest):
        # remember a connecting client so that data can be received or broadcast to that connection
        if clientTypeRequest == 'surface':
            self.surfaceConnection = client # surface sends joystick data

        elif clientTypeRequest == 'motor':
            self.motorConnection = client # motor receives joystick data

        elif clientTypeRequest == 'miniROV':
            self.miniMotorConnection = client # mini-rov recives joystick data

        else:
            print('Bad client type received: {}'.format(clientTypeRequest))
            client._closeConnection() # find some better way to end the connection; unclean closing

    def unregister(self, client):
        # remove a remembered connection
        if self.surfaceConnection == client:
            self.surfaceConnection = None

        elif self.motorConnection == client:
            self.motorConnection = None

        elif self.miniMotorConnection == client:
            self.miniMotorConnection = None

        else:
            print('Unknown client: {}'.format(client))

    def broadcast(self, client, msg, isBinary):
        # broacast data to other connections

        # only surface pi is supposed to send data
        if self.surfaceConnection == client:
            # broadcasting

            if self.motorConnection:
                self.motorConnection.sendMessage(msg)

            if self.miniMotorConnection:
                self.miniMotorConnection.sendMessage(msg)

        elif self.motorConnection == client:
            print('Motor Pi isn\'t supposed to send stuff')

        elif self.miniMotorConnection == client:
            print('Mini ROV isn\'t supposed to send stuff')


log.startLogging(sys.stdout) # TODO: replace with log file (maybe)

# Setup server factory
server = ServerFactory(u'ws://{}:{}'.format(IP , PORT))
server.protocol = ServerProtocol

reactor.listenTCP(PORT, server)

try:
    reactor.run()
finally:
    pass # f.close()
