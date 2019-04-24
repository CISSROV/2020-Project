#!/bin/bash

echo 'Connecting to motor pi...'
sshpass -p raspberry ssh pi@192.168.1.4 python3 motor2020.py