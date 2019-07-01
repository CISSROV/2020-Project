#!/usr/bin/env python3.4
# Author: Jonathan Rotter

#
# This module required for motor2020 and surface2020
# and thus is needed on both motor pi and surface pi.
# It handles the websocket stuff for both those programs.
# 
# Required 3rd-party libraries:
# autobahn
# twisted
# 

# websocket stuff
from autobahn.twisted.websocket import \
    WebSocketClientProtocol, WebSocketClientFactory

import sys

# asyncronous stuff
from twisted.python import log
from twisted.internet import task, reactor

# ip is localhost, does not need to be changed
IP = '127.0.0.1'
# needs the be the same here as in server2020
PORT = 8008

# time between surface2020 being run in seconds
# frequency = 1/timeout
TIMEOUT = 0.1

#
# How to use
# start( 'motor' or 'surface', func )
# if motor, func should take one string arg
# if surface, func should return a string
# func is a refrence to a function, so NO parentheses next to it
# dont call it, pass the refrence to the function itself
#

class ClientProtocol(WebSocketClientProtocol):
    #
    # Determines how the client will communicate with the server
    #

    def onConnect(self, response):
        # called by the client factory
        print("Server connected: {0}".format(response.peer))
        # remember this connection
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
        # payload is encoded (bytes-like object)

        # validate that the type is motor2020 or miniROV
        # surface2020 shouldn't receive data
        if self.factory.clientType in ['motor', 'miniROV']:
            # received instructions!
            # decode bytes to string
            txt = payload.decode()
            # call the given function, passing the 
            # payload/message as an argument
            self.factory.func(txt)

        else:
            # fail fast for debugging purposes
            raise ValueError('Only motor pi / Mini ROV should receive data')


    def onClose(self, wasClean, code, reason):
        # called by the client factory
        print("WebSocket connection closed: {0}".format(reason))
        # remove the remembered connection
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

        # get data by calling the given function
        txt = self.func()
        for c in self.connections:
            # send that data to the connected clients
            c.sendMessage(txt.encode())

    def clientConnectionFailed(self, connector, error):
        #reactor.stop()
        self.connectionRefusedCount += 1
        for _ in range(2):
            # clears two lines in the console
            # don't know why though
            print('\r\033[K\033[A', end='')
        print(self.connectionRefusedCount, error.getErrorMessage())

        # try to connect again in 3 seconds
        reactor.callLater(3, connectTCP, self)

def connectTCP(factory):
    global IP, PORT
    # connect to the ip and port
    reactor.connectTCP(IP, PORT, factory)

def start(clientType, func, ip=None):
    # when the module is imported by motor2020 or surface2020,
    # those files call this method to use this module
    # clientType specifies whether it is motor2020 or surface2020
    global IP
    if ip:
        # set the default ip (localhost) to the given ip if it is specified
        IP = ip

    # display debug info on stdout
    log.startLogging(sys.stdout)

    # new factory object
    factory = ClientFactory(
            u'ws://{}:{}/{}'.format(IP , PORT, clientType),
            clientType,
            func
        )
    factory.protocol = ClientProtocol

    #reactor.connectTCP(IP, PORT, factory)

    connectTCP(factory)

    if clientType == 'surface':
        # if this us type surface, start a loop where every TIMEOUT number of seconds
        # it runs the given function to get the data and send it off
        l = task.LoopingCall(factory.broadcast) # only for surface
        l.start(TIMEOUT)

    # start the code
    reactor.run()

if __name__ == '__main__':
    # not to be run as the main module
    raise Exception('This code is only to be imported!!!')
