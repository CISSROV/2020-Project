#!/usr/bin/env python3.4
# Author: Jonathan Rotter

from autobahn.twisted.websocket import \
    WebSocketClientProtocol, WebSocketClientFactory

import sys
from twisted.python import log
from twisted.internet import task, reactor

# ip is localhost
IP = '127.0.0.1'
PORT = 8008

# time between surface2020 being run
# frequency = 1/timeout
TIMEOUT = 0.1

#
# How to use
# start( 'motor' or 'surface', func )
# if motor, func should take one string arg
# if surface, func should return a string
#

class ClientProtocol(WebSocketClientProtocol):
    #
    # Determines how the client will communicate with the server
    #

    def onConnect(self, response):
        # called by the client factory
        print("Server connected: {0}".format(response.peer))
        self.factory.register(self)

    def onConnecting(self, transport_details):
        # called by the client factory
        print("Connecting; transport details: {}".format(transport_details))
        return None

    def onOpen(self):
        # called by the client factory
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        # called by the client factory
        # payload is encoded
        if self.factory.clientType in ['motor', 'miniROV']:
            # received instructions!
            txt = payload.decode()
            self.factory.func(txt)

        else:
            raise ValueError('Only motor pi / Mini ROV should receive data')


    def onClose(self, wasClean, code, reason):
        # called by the client factory
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.unregister(self)

class ClientFactory(WebSocketClientFactory):
    #
    # Determines how connection deal with each other
    #

    def __init__(self, url, clientType, func):
        # url is a string in the format "ws://127.0.0.1:8008"
        # clientType is the string "/motor"
        # func is the handler function
        WebSocketClientFactory.__init__(self, url)
        self.connections = []
        self.clientType = clientType
        self.func = func
        self.connectionRefusedCount = 0

    def register(self, client):
        # remember this connection
        if client not in self.connections:
            self.connections.append(client)

    def unregister(self, client):
        # forget this connection
        if client in self.connections:
            self.connections.remove(client)

    def broadcast(self): # only for surface
        # send to all other connections
        if not len(self.connections):
            return # no connections

        if self.clientType != 'surface':
            raise ValueError('Only surface py should broadcast data')

        # ???
        txt = self.func()
        for c in self.connections:
            c.sendMessage(txt.encode())

    def clientConnectionFailed(self, connector, error):
        #reactor.stop()
        self.connectionRefusedCount += 1
        for _ in range(2):
            print('\r\033[K\033[A', end='')
        print(self.connectionRefusedCount, error.getErrorMessage())
        reactor.callLater(3, connectTCP, self)

def connectTCP(factory):
    global IP, PORT
    reactor.connectTCP(IP, PORT, factory)

def start(clientType, func, ip=None):
    global IP
    if ip:
        IP = ip

    log.startLogging(sys.stdout)

    factory = ClientFactory(
            u'ws://{}:{}/{}'.format(IP , PORT, clientType),
            clientType,
            func
        )

    factory.protocol = ClientProtocol

    #reactor.connectTCP(IP, PORT, factory)
    connectTCP(factory)

    if clientType == 'surface':
        l = task.LoopingCall(factory.broadcast) # only for surface
        l.start(TIMEOUT)

    reactor.run()

if __name__ == '__main__':
    raise Exception('This code is only to be imported!!!')
