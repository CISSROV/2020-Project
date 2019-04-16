#!/bin/bash

if [[ $1 == 'start' ]]
then
    echo "Startup!"

    # start cmd: sudo /var/www/scripts/dataCollection.sh start
    # ssh cmd: sshpass -p raspberry ssh pi@192.168.1.3 ls

    # starts the data collection code on camera pi
    # webSocket.py to be specific
    sshpass -p raspberry ssh pi@192.168.1.3 sudo /var/www/scripts/dataCollection.sh start

elif [[ $1 == 'stop' ]]
then
    echo "Shutdown!"

    sshpass -p raspberry ssh pi@192.168.1.3 sudo /var/www/scripts/dataCollection.sh stop
else
    echo "Usage: startup.sh [start|stop]"
fi

