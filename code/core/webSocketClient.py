#!/usr/bin/env python3.4
'''Author: Jonathan Rotter

This module is required for motor2020 and surface2020
and thus needs to be on both motor pi and surface pi.
It handles the websocket stuff for both those programs.


How to use:
    start( 'motor' or 'surface', func )
    if motor, func should take one string arg
    if surface, func should return a string
    func is a reference to a function, so NO parentheses next to it
    don't call it, pass the reference to the function itself


Required 3rd-party libraries:
`autobahn`
`twisted`
'''

# websocket stuff
from autobahn.twisted.websocket import \
    WebSocketClientProtocol, WebSocketClientFactory

import sys

# asynchronous stuff
from twisted.python import log
from twisted.internet import task, reactor

IP = '127.0.0.1'
'''ip is localhost, does not need to be changed'''

PORT = 8008
'''needs the be the same here as in server2020'''

# frequency = 1/timeout
TIMEOUT = 0.1
'''time between surface2020 being run in seconds'''


class ClientProtocol(WebSocketClientProtocol):
    '''
    Determines how the client will communicate with the server
    '''

    def onConnect(self, response):
        '''
        Called by the client factory when
        connecting
        '''
        print("Server connected: {0}".format(response.peer))
        # remember this connection
        self.factory.register(self)

    def onConnecting(self, transport_details):
        '''
        Called by the client factory when
        connecting
        '''
        print("Connecting; transport details: {}".format(transport_details))
        return None

    def onOpen(self):
        '''
        Called by the client factory when
        the connection is open
        '''
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        '''
        Called by the client factory when
        receiving a message

        Args:
            payload (bytes): A bytes-like object
            isBinary (bool): Almost always true
        '''

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
        '''
        Called by the client factory when closing
        '''

        print("WebSocket connection closed: {0}".format(reason))
        # remove the remembered connection
        self.factory.unregister(self)


class ClientFactory(WebSocketClientFactory):
    '''
    Determines how connections deal with each other
    '''

    def __init__(self, url, clientType, func):
        '''
        Initializes the class

        Args:
            url (str): The url in the format "ws://127.0.0.1:8008"
            clientType (str): Example: "/motor"
            func (function): The handler function
        '''

        WebSocketClientFactory.__init__(self, url)
        self.connections = []
        self.clientType = clientType
        self.func = func
        self.connectionRefusedCount = 0

    def register(self, client):
        '''
        Called in `ClientProtocol.onConnect`
        Remember this connection
        '''
        if client not in self.connections:
            self.connections.append(client)

    def unregister(self, client):
        '''
        Called in `ClientProtocol.onClose`
        Forget this connection
        '''
        if client in self.connections:
            self.connections.remove(client)

    def broadcast(self):
        '''
        Send a message to all other connections
        Only for surface pi
        '''

        if not len(self.connections):
            return  # no connections

        if self.clientType != 'surface':
            raise ValueError('Only surface py should broadcast data')

        # get data by calling the given function
        txt = self.func()
        for c in self.connections:
            # send that data to the connected clients
            c.sendMessage(txt.encode())

    def clientConnectionFailed(self, connector, error):
        '''
        Called automatically when a connection
        fails. Tells the reactor (Twisted's event manager)
        to try to reconnect in 3 seconds
        '''
        self.connectionRefusedCount += 1
        for _ in range(2):
            # clears two lines in the console
            print('\r\033[K\033[A', end='')
        print(self.connectionRefusedCount, error.getErrorMessage())

        # try to connect again in 3 seconds
        reactor.callLater(3, connectTCP, self)


def connectTCP(factory):
    '''Tries to connect to the given IP and Port number'''
    global IP, PORT

    # connect to the ip and port
    reactor.connectTCP(IP, PORT, factory)


def start(clientType, func, ip=None):
    '''
    Called by motor2020 or surface2020
    to use this module

    Args:
        clientType (str): Specifies whether it is motor pi or surface pi
        func (function): The handler for messages
        ip (str, optional): The ip address

    '''
    global IP
    if ip:
        # set the default ip (localhost) to the given ip if it is specified
        IP = ip

    # display debug info on stdout
    log.startLogging(sys.stdout)

    # new factory object
    factory = ClientFactory(
            u'ws://{}:{}/{}'.format(IP, PORT, clientType),
            clientType,
            func
        )
    factory.protocol = ClientProtocol

    # reactor.connectTCP(IP, PORT, factory)

    connectTCP(factory)

    if clientType == 'surface':
        # if this us type surface, start a loop where every TIMEOUT number of seconds
        # it runs the given function to get the data and send it off
        l = task.LoopingCall(factory.broadcast)  # only for surface
        l.start(TIMEOUT)

    # start the code
    reactor.run()


if __name__ == '__main__':
    # not to be run as the main module
    raise Exception('This code is only to be imported!!!')
