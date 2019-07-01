#!/usr/bin/env python3.4

# 3rd-party library called autobahn for websocket stuff
# autobahn requires twisted 
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

import sys
import time
import json
import os

# 3rd-party library called twisted for asyncronous
from twisted.python import log
from twisted.internet import task, reactor

# --- !!!  IMPORTANT  !!! --- This process is - and must be - run and owned by root

import dataCollectShards as dataShards

try:
    # try setting up the sensors
    dataShards.setup()
except Exception as e:
    print(e)
    sys.exit(1)
else:
    print('Successful Gyroscope Startup')

def getDateISO8601():
    # return date in YYYY-MM-DD
    tmp = time.localtime()
    return '{}-{:0>2}-{:0>2}'.format(tmp.tm_year, tmp.tm_mon, tmp.tm_mday)

# make sure all ports are set to be the same
IP = '127.0.0.1'
PORT = 5005

# then use getDataFragment()

#  --- !!!  IMPORTANT  !!! --- the serial connection must be set up BEFORE the twisted stuff
# because upon hitting an error it must shutdown the program and should not be ingored or silenced
# cause twisted does that
# if handled it must call sys.exit or something else to terminate the program

# Fetch data every x seconds
timeout = 1.0 # in seconds

class ServerProtocol(WebSocketServerProtocol):
    # object created for each connection

    def onConnect(self, request):
        # called when someone connects

        print('Client connecting & registering: {0}'.format(request.peer))
        # remember the connection
        self.factory.register(self)

    def onOpen(self):
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        # called when the connection is closed

        print('WebSocket connection closed & unregistering: {0}'.format(reason))
        # forget the connection
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        # called when receiving a message

        #
        # for debugging, sending hi to this server 
        # prompts a response of Hellow World!
        # Used to determine whenever a connection to this server is alive and good
        #
        if msg == b'hi':
            self.sendMessage(b'Hello World!')

class ServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        # list of clients / remembered connections
        self.clients = []

    def register(self, client):
        # add a client if not yet in the list
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        # remove a client if in the list
        if client in self.clients:
            self.clients.remove(client)

    def broadcast(self):
        # call to get sensor data and send to all clients

        # collect sensor data and turn it into a json string
        msg = json.dumps(dataShards.getDataFragment())

        print("broadcasting message '{}' ..".format(msg))

        # send the data to each client
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))

# get date in YYYY-MM-DD
date = getDateISO8601()

#
# Log files are locating in /var/log/MATE/
# and have the name websocketYYYY-MM-DD.log where the date is the day
# the code was run and the log file created
# As the raspberry pis don't actually have the right time this date may be off
#

try:
    # try to open the log file in appending mode
    f = open('/var/log/MATE/websocket{}.log'.format(date), 'a')
except FileNotFoundError:
    # if the log file doesn't exist yet, make a new one and open that one
    f = open('/var/log/MATE/websocket{}.log'.format(date), 'w')

# start sending info to the log file
log.startLogging(f)

# url in the format of ws://127.0.0.1:5005
server = ServerFactory(u'ws://{}:{}'.format(IP , PORT)) # update this! <- Note: idk why this
server.protocol = ServerProtocol

# listen for tcp connections on the port
reactor.listenTCP(PORT, server)

# wait till the next whole 5 seconds
time.sleep(abs(time.time() % -5)) 

# this doesn't seem to have a purpose
starttime = time.time()

# call server.broadcast() every timeout number of seconds to broadcast sensor data to clients
l = task.LoopingCall(server.broadcast)
l.start(timeout)

try:
    # start doing stuff
    reactor.run()
finally:
    # close the file no matter what
    f.close()
