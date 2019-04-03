#!/bin/bash

cd /var/www/scripts
nohup sudo python3.4 dataCollector.py > out.log &

tmp=$(pgrep -f "sudo python3.4 dataCollector.py")

echo "PID: $tmp"