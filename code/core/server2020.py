#!/usr/bin/env python3.4
# Author: Jonathan Rotter

#
# Server code
#
# To be run on server pi. It is required (source?) that
# it is started before motor2020++.py or surface2020.py
# 
# Once it is running it does not need to be restarted 
# even if its clients restart or lose connection
#
# 
# Required 3rd-party libraries:
# autobahn
# twisted
# 

# Check if the version of python is 3.x
import sys
if sys.version[0] != '3':
    # Stop running if the version is python 2.x 
    raise Exception('This is Python3 code')

# importing the neccesary objects
# autobahn does websocket stuff, but relies on twisted
from autobahn.twisted.websocket import \
    WebSocketServerProtocol, WebSocketServerFactory

# twisted does asyncronous code execution needed for websockets
from twisted.python import log
from twisted.internet import task, reactor

# ip is localhost, does not need to be changed
IP = '127.0.0.1'
# Make sure the port set here and in webSocketClient are the same
PORT = 8008

class ServerProtocol(WebSocketServerProtocol):
    #
    # Describes how the websocket server should act
    # with one connection
    #
    # How to connect to it in JavaScript
    # ws = new WebSocket('ws://localhost:8008/motor')
    # ws = new WebSocket('ws://localhost:8008/surface')
    #

    def onConnect(self, request):
        # called by the server factory
        # the path is used for the clients to specify whether they are motor2020 or surface2020
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
        # called by the server factory
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        # called by the server factory
        print('WebSocket connection closed & unregistering: {0}'.format(reason))

        # tell the factory that this connection is dead
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        # called by the server factory

        # tell the factory to broadcast the received message to all other connected clients
        self.factory.broadcast(self, msg, isBinary)

class ServerFactory(WebSocketServerFactory):
    #
    # Keeps track of all connections and relays data to other clients
    #

    def __init__(self, url):
        # url has to be in the format of "ws://127.0.0.1:8008"
        WebSocketServerFactory.__init__(self, url)

        # init fields
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
            # end the connection because the client's type is not recognized
            # the type the client is is specified by the path in the url
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


# display debug information to stdout for now
log.startLogging(sys.stdout) # TODO: replace with log file (maybe)

# Setup server factory
server = ServerFactory(u'ws://{}:{}'.format(IP , PORT))
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
