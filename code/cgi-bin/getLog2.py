#!/usr/bin/env python3.4
import time

print("Content-type: text/html\n\n")

try:
    f = open('/var/www/scripts/nohup.out', 'r')
    raw = f.read()
    f.close()

    raw = raw.replace('\n', '<br>')

    print(raw)
except FileNotFoundError as e:
    print(e)
