from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred

'''
from twisted.internet import task, reactor

timeout = 60.0 # Sixty seconds

def doWork():
    #do work here
    pass

l = task.LoopingCall(doWork)
l.start(timeout) # call every sixty seconds

reactor.run()
'''

import dataCollectionPieces as dataShards
try:
    dataShards.setup()
except Exception as e:
    print(e)
    sys.exit(1)
else:
    print('Successful Gyroscope Startup')

# then use getDataFragment()

# Fetch data every x seconds
timeout = 5.0 # in seconds


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
