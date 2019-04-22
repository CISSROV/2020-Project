#!/usr/bin/env python3.4
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

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

THIS_TYPE = CLIENT_TYPES[1] # 0 - motor, 1 - surface

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
        if THIS_TYPE == 'motor':
            # recv instructions!
            print(payload)
            txt = payload.decode()
            self.factory.func(txt)
        else:
            raise ValueError('Only motor py should receive data')


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.unregister(self)

class ClientFactory(WebSocketClientFactory):

    def __init__(self, url, func):
        WebSocketClientFactory.__init__(self, url)
        self.connections = []
        self.func = func

    def register(self, client):
        if client not in self.connections:
            self.connections.append(client)

    def unregister(self, client):
        if client in self.connections:
            self.connections.remove(client)

    def broadcast(self): # only for surface
        global THIS_TYPE
        if THIS_TYPE != 'surface':
            raise ValueError('Only surface py should broadcast data')
        print('ping')
        txt = self.factory.func()
        for c in self.connections:
            c.sendMessage(txt.encode())


log.startLogging(sys.stdout)

factory = ClientFactory(u'ws://{}:{}/surface'.format(IP , PORT), func)
factory.protocol = ClientProtocol

reactor.connectTCP(IP, PORT, factory)

if THIS_TYPE == 'surface':
    l = task.LoopingCall(factory.broadcast) # only for surface
    l.start(TIMEOUT)

reactor.run()
