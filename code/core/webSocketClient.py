#!/usr/bin/env python3.4
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

import sys
from twisted.python import log
from twisted.internet import task, reactor

IP = '127.0.0.1'
PORT = 8008

TIMEOUT = 0.1

clientTypes = [
    'motor',
    'surface'
]

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
        print(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.factory.unregister(self)

class ClientFactory(WebSocketClientFactory):

    def __init__(self, url):
        WebSocketClientFactory.__init__(self, url)
        self.connections = []

    def register(self, client):
        if client not in self.connections:
            self.connections.append(client)

    def unregister(self, client):
        if client in self.connections:
            self.connections.remove(client)


    def broadcast(self):
        print('ping')
        for c in self.connections:
            c.sendMessage(b'Hello World!')


log.startLogging(sys.stdout)

factory = ClientFactory(u'ws://{}:{}/surface'.format(IP , PORT))
factory.protocol = ClientProtocol

reactor.connectTCP(IP, PORT, factory)

l = task.LoopingCall(factory.broadcast)
l.start(TIMEOUT)

reactor.run()
