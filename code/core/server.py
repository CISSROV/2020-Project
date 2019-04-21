#!/usr/bin/env python3.4
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

import sys
import time
import json
from twisted.python import log
from twisted.internet import task, reactor

IP = '127.0.0.1'
PORT = 8008

clientTypes = [
    'motor',
    'surface'
]

class ServerProtocol(WebSocketServerProtocol):
    # ws = new WebSocket('ws://localhost:8008/motor')
    # ws = new WebSocket('ws://localhost:8008/surface')

    def onConnect(self, request):
        print(request.path)
        print(request)
        print('Client connecting & registering: {0}'.format(request.peer))
        clientTypeRequest = request.path
        if clientTypeRequest.startswith('/'):
            clientTypeRequest = clientTypeRequest[1:]

        if clientTypeRequest not in clientTypes:
            print('Bad client type received: {}'.format(clientTypeRequest))
            self._closeConnection() # find smth better; unclean closing
        else:
            self.factory.register(self, clientTypeRequest)

    def onOpen(self):
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        print('WebSocket connection closed & unregistering: {0}'.format(reason))
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        print(msg, isBinary)

class ServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.surfaceConnection = None

    def register(self, client, clientTypeRequest):
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def broadcast(self):
        msg = json.dumps(dataShards.getDataFragment())
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))

log.startLogging(sys.stdout) # replace with log file

server = ServerFactory(u'ws://{}:{}'.format(IP , PORT)) # update this!
server.protocol = ServerProtocol

reactor.listenTCP(PORT, server)

try:
    reactor.run()
finally:
    pass # f.close()
