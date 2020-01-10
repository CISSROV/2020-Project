#!/usr/bin/env python3.4
'''
Author: Jonathan Rotter

Makes a websocket server that broadcasts
the sensor data from the ROV to any connected
client. It is used in the webpage to display
sensor data.

 --- !!!  IMPORTANT  !!! ---
    This process HAS TO BE RUN AS ROOT (with sudo)
    for it to function properly

    Also the serial connection must be set up BEFORE the twisted stuff
    because upon hitting an error it must shutdown the program and
    should not be ignored or silenced because twisted will do that
    if handled it must call sys.exit or something else to terminate the program

Required 3rd-party libraries:
`autobahn`
`twisted`
'''

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import sys
import time
import json

# 3rd-party library called twisted for asynchronous
from twisted.python import log
from twisted.internet import task, reactor

# --- !!!  IMPORTANT  !!! --- This process must be - run and owned by root

if __name__ == '__main__':
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
    '''
    Gets the current date in the format YYYY-MM-DD

    Return:
        date: In the format of YYYY-MM-DD
    '''
    tmp = time.localtime()
    return '{}-{:0>2}-{:0>2}'.format(tmp.tm_year, tmp.tm_mon, tmp.tm_mday)


IP = '127.0.0.1'
'''
The IP of the server.
Can be set to localhost and it will still work
'''
PORT = 5005
'''
Make sure systems using this server as their data source
are set to the right port
'''

# then use getDataFragment()

#  --- !!!  IMPORTANT  !!! --- the serial connection must be set up BEFORE the twisted stuff
# because upon hitting an error it must shutdown the program and should not be ignored or silenced
# cause twisted does that
# if handled it must call sys.exit or something else to terminate the program

# Fetch data every x seconds
timeout = 1.0  # in seconds
'''Time in seconds it should wait between fetching data'''


class ServerProtocol(WebSocketServerProtocol):
    '''
    Object created for each connection. It handles
    the communcation with one client.
    '''

    def onConnect(self, request):
        '''
        Called automatically when someone connects.
        Adds them to the list of connections and prints debug info
        '''

        print('Client connecting & registering: {0}'.format(request.peer))
        # remember the connection
        self.factory.register(self)

    def onOpen(self):
        '''
        Called automatically when someone connects.
        Prints debug info
        '''
        print('WebSocket connection open')

    def onClose(self, wasClean, code, reason):
        '''
        Called automatically when someone disconnects.
        Prints debug info and removes them from the list of connected clients
        '''

        print('WebSocket connection closed & unregistering: {0}'.format(reason))
        # forget the connection
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        '''
        Called automatically when a message is received
        Only used for debugging.
        If sent `hi`, the server will respond with `Hello World!`.
        This feature is used to determine whenever a connection
        to this server is alive and good
        '''

        if msg == b'hi':
            self.sendMessage(b'Hello World!')


class ServerFactory(WebSocketServerFactory):
    '''
    Keeps track of all connections and
    broadcasts sensor data to them
    '''

    def __init__(self, url):
        '''
        Initializes the class

        Arg:
            url (str): Should be in the format ws://127.0.0.1:5005
        '''
        WebSocketServerFactory.__init__(self, url)
        # list of clients / remembered connections
        self.clients = []

    def register(self, client):
        '''
        Called by `ServerProtocol.onConnect`
        to add a client to the list of clients
        '''

        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        '''
        Called by `ServerProtocol.onClose`
        to remove a client from the list of clients
        '''

        if client in self.clients:
            self.clients.remove(client)

    def broadcast(self):
        '''
        Calls `dataShards.getDataFragment` to get
        sensor data and then sends that data to
        all connected clients as in json.
        '''

        # collect sensor data and turn it into a json string
        msg = json.dumps(dataShards.getDataFragment())

        print("broadcasting message '{}' ..".format(msg))

        # send the data to each client
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))

# get date in YYYY-MM-DD
date = getDateISO8601()
'''Today's date in YYYY-MM-DD, fetched from `getDateISO8601`'''


#
# Log files are locating in /var/log/MATE/
# and have the name websocketYYYY-MM-DD.log where the date is the day
# the code was run and the log file created
# As the raspberry pis don't actually have the right time this date may be off
#

if __name__ == '__main__':
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
