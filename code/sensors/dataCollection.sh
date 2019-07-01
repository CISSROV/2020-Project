#!/bin/bash

#
# This script combines startDataCollection.sh and stopDataCollection.sh 
# into one file to reduce clutter
# It is to start the webSocketServer used to collect and share sensor data
#

cd /var/www/scripts

# if the first argument is start
if [[ $1 == 'start' ]]
then
    echo "Startup!"

    # nohup and the ampersand (&) make it run in the background
    # even if the user closes the terminal window or ssh connection
    nohup sudo python3.4 webSocketServer.py &

    # find the process id of it
    tmp=$(pgrep -f "sudo python3.4 webSocketServer.py")

    # display the process id
    echo "PID: $tmp"

# if the first argument is stop
elif [[ $1 == 'stop' ]]
then
    echo "Shutdown!"

    # find the process id
    tmp=$(pgrep -f "sudo python3.4 webSocketServer.py")

    # if $tmp isn't a number because the PID couldn't be found
    if [ -z $tmp ]
    then
        echo "It seems that the code isn't running"
        echo "Try usning ps -eaf | grep python to find it"
        exit 1
    else
        #
        # send an interrupt to allow the code to shutdown gently
        # and a second later send a kill to complete get
        # rid of the process
        # Otherwise it lingers around in a halted state
        #
        echo PID: $tmp
        sudo kill -s SIGINT $tmp
        sleep 1
        sudo kill -s SIGKILL $tmp
    fi

    # for some reason the sudo command and the command as root
    # have seperate PIDs so just kill both

    # find the process id
    tmp=$(pgrep -f "python3.4 webSocketServer.py")

    # if $tmp isn't a number because the PID couldn't be found
    if [ -z $tmp ]
    then
        exit 1
    else
        #
        # send an interrupt to allow the code to shutdown gently
        # and a second later send a kill to complete get
        # rid of the process
        # Otherwise it lingers around in a halted state
        #
        echo PID: $tmp
        sudo kill -s SIGINT $tmp
        sleep 1
        sudo kill -s SIGKILL $tmp
    fi
else
    # first argument not start or stop
    echo "Usage: dataCollection.sh [start|stop]"
fi
