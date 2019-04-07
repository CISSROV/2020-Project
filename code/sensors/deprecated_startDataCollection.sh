#!/bin/bash

cd /var/www/scripts

if [ $? -eq 0 ]
then
    echo 'OK'
else
    echo 'Error Code' $?
    exit 1
fi

nohup sudo python3.4 dataCollection.py > out.log &

if [ $? -eq 0 ]
then
    echo 'OK'
else
    echo 'Error Code' $?
    exit 1
fi

tmp=$(pgrep -f "sudo python3.4 dataCollection.py")

echo "PID: $tmp"
