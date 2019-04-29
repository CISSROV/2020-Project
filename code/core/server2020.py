#!/usr/bin/env python3.4

import sys
if sys.version[0] != '3':
    raise Exception('This is Python3 code')

from autobahn.twisted.websocket import \
    WebSocketServerProtocol, WebSocketServerFactory

from twisted.python import log
from twisted.internet import task, reactor


IP = '127.0.0.1'
PORT = 8008

class ServerProtocol(WebSocketServerProtocol):
    # ws = new WebSocket('ws://localhost:8008/motor')
    # ws = new WebSocket('ws://localhost:8008/surface')

    def onConnect(self, request):
        print(request.path)
        print('Client connecting & registering: {0}'.format(request.peer))
        clientTypeRequest = request.path
        if clientTypeRequest.startswith('/'):
            clientTypeRequest = clientTypeRequest[1:]

        self.factory.register(self, clientTypeRequest)

    def onOpen(self):
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        print('WebSocket connection closed & unregistering: {0}'.format(reason))
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        self.factory.broadcast(self, msg, isBinary)

class ServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.motorConnection = None
        self.miniMotorConnection = None
        self.surfaceConnection = None

    def register(self, client, clientTypeRequest):
        if clientTypeRequest == 'surface':
            self.surfaceConnection = client

        elif clientTypeRequest == 'motor':
            self.motorConnection = client

        elif clientTypeRequest == 'miniROV':
            self.miniMotorConnection = client

        else:
            print('Bad client type received: {}'.format(clientTypeRequest))
            client._closeConnection() # find smth better; unclean closing

    def unregister(self, client):
        if self.surfaceConnection == client:
            self.surfaceConnection = None

        elif self.motorConnection == client:
            self.motorConnection = None

        elif self.miniMotorConnection == client:
            self.miniMotorConnection = None

        else:
            print('Unknown client: {}'.format(client))

    def broadcast(self, client, msg, isBinary):
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


log.startLogging(sys.stdout) # replace with log file (maybe)

server = ServerFactory(u'ws://{}:{}'.format(IP , PORT))
server.protocol = ServerProtocol

reactor.listenTCP(PORT, server)

try:
    reactor.run()
finally:
    pass # f.close()
