#!/bin/bash

tmp=$(pgrep -f "sudo python3.4 dataCollection.py")


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

tmp=$(pgrep -f "python3.4 dataCollection.py")

if [ -z $tmp ]
then
    exit 1
else
    echo PID: $tmp
    sudo kill -s SIGINT $tmp
    sleep 1
    sudo kill -s SIGKILL $tmp
fi

#ps -eaf | grep python | less
# useless as it takes a while to shutdown the child process
