#!/usr/bin/env python3.4
from autobahn.twisted.websocket import \
    WebSocketClientProtocol, WebSocketClientFactory

import sys
from twisted.python import log
from twisted.internet import task, reactor

IP = '127.0.0.1'
PORT = 8008

TIMEOUT = 0.1

CLIENT_TYPES = [
    'motor',
    'surface' # surface code
]

#
# How to use
# start( 'motor' or 'surface', func )
# if motor, func should take one string arg
# if surface, func should return a string
#

class ClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.factory.register(self)

    def onConnecting(self, transport_details):
        print("Connecting; transport details: {}".format(transport_details))
        return None

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if self.factory.clientType == 'motor':
            # recv instructions!
            txt = payload.decode()
            self.factory.func(txt)
        else:
            raise ValueError('Only motor py should receive data')


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.unregister(self)

class ClientFactory(WebSocketClientFactory):

    def __init__(self, url, clientType, func):
        WebSocketClientFactory.__init__(self, url)
        self.connections = []
        self.clientType = clientType
        self.func = func
        self.connectionRefusedCount = 0

    def register(self, client):
        if client not in self.connections:
            self.connections.append(client)

    def unregister(self, client):
        if client in self.connections:
            self.connections.remove(client)

    def broadcast(self): # only for surface
        if not len(self.connections):
            return # no connections

        if self.clientType != 'surface':
            raise ValueError('Only surface py should broadcast data')

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

    if clientType not in CLIENT_TYPES:
        raise ValueError('Client Type is not surface or motor: {}'.format(clientType))

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
