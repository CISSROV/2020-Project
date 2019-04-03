#!/bin/bash

tmp=$(pgrep -f "sudo python3.4 dataCollector.py")


if [ -z $tmp ]
then
    echo "It seems that the code isn't running"
    echo "Try usning ps -eaf | grep python to find it"
else
    echo PID: $tmp
    sudo kill -s SIGINT $tmp
fi

#ps -eaf | grep python | less
# useless as it takes a while to shutdown the child process


