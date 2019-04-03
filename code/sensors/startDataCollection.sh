#!/bin/bash

cd /var/www/scripts
nohup sudo python3.4 dataCollection.py > out.log &

tmp=$(pgrep -f "sudo python3.4 dataCollection.py")

echo "PID: $tmp"
