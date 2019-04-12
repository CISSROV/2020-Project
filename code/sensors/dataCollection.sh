#!/bin/bash

# This script combines startDataCollection.sh and stopDataCollection.sh into one file to reduce clutter

cd /var/www/scripts

if [[ $1 == 'start' ]]
then
    echo "Startup!"

    nohup sudo python3.4 webSocketServer.py &

    # old file -> dataCollection.py
    tmp=$(pgrep -f "sudo python3.4 webSocketServer.py")

    echo "PID: $tmp"

elif [[ $1 == 'stop' ]]
then
    echo "Shutdown!"

    tmp=$(pgrep -f "sudo python3.4 webSocketServer.py")

    if [ -z $tmp ]
    then
        echo "It seems that the code isn't running"
        echo "Try usning ps -eaf | grep python to find it"
        exit 1
    else
        echo PID: $tmp
        sudo kill -s SIGINT $tmp
        sleep 1
        sudo kill -s SIGKILL $tmp
    fi

    tmp=$(pgrep -f "python3.4 webSocketServer.py")

    if [ -z $tmp ]
    then
        exit 1
    else
        echo PID: $tmp
        sudo kill -s SIGINT $tmp
        sleep 1
        sudo kill -s SIGKILL $tmp
    fi
else
    echo "Usage: dataCollection.sh [start|stop]"
fi
