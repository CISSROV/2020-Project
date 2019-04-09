from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import sys
from twisted.python import log
from twisted.internet import task, reactor
from twisted.internet.defer import Deferred

'''
import dataCollectionPieces as dataShards
try:
    dataShards.setup()
except Exception as e:
    print(e)
    sys.exit(1)
else:
    print('Successful Gyroscope Startup')
'''

# then use getDataFragment()

# Fetch data every x seconds
timeout = 5.0 # in seconds

class ServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        #print(request.path, request.protocols)
        print('Client connecting & registering: {0}'.format(request.peer))
        self.factory.register(self)

    def onOpen(self):
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        print('WebSocket connection closed & unregistering: {0}'.format(reason))
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        if isBinary:
            print('Error: Should not get binary')
        else:
            print('Text message received: {0}'.format(msg.decode('utf8')))

        #msg = s.encode('utf8')
        self.sendMessage(msg, isBinary)

class ServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)

    def broadcast(self):
        msg = str(pseudoGetData())
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))

log.startLogging(sys.stdout)

server = ServerFactory(u'ws://127.0.0.1:5006')
server.protocol = ServerProtocol

reactor.listenTCP(5006, server)

l = task.LoopingCall(server.broadcast)
l.start(timeout)

reactor.run()
