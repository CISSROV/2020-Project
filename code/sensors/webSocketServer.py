
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import sys
from twisted.python import log
from twisted.internet import reactor

class WebSocketServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print('Client connecting: {0}'.format(request.peer))

    def onOpen(self):
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        print('WebSocket connection closed: {0}'.format(reason))

    def onMessage(self, msg, isBinary):
        if isBinary:
            print('Error: Should not get binary')
        else:
            print('Text message received: {0}'.format(msg.decode('utf8')))

        self.sendMessage(msg, isBinary)

    

log.startLogging(sys.stdout)

server = WebSocketServerFactory(u'ws://127.0.0.1:5005')
server.protocol = WebSocketServerProtocol

reactor.listenTCP(5005, server)
reactor.run()
