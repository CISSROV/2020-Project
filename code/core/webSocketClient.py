#!/usr/bin/env python3.4
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

import sys
from twisted.python import log
from twisted.internet import reactor

IP = '127.0.0.1'
PORT = 8008

clientTypes = [
    'motor',
    'surface'
]

class ClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onConnecting(self, transport_details):
        print("Connecting; transport details: {}".format(transport_details))
        return None

    def onOpen(self):
        print("WebSocket connection open.")

        def sendData():
            self.sendMessage("nothing")
            self.factory.reactor.callLater(1, sendData) # improve this

        hello()

    def onMessage(self, payload, isBinary):
        pass

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


log.startLogging(sys.stdout)

factory = WebSocketClientFactory(u'ws://{}:{}/surface'.format(IP , PORT))
factory.protocol = ClientProtocol

reactor.connectTCP(IP, PORT, factory)
reactor.run()
