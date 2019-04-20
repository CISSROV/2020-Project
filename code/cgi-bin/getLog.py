#!/usr/bin/env python3.4
import time

def getDateISO8601():
    tmp = time.localtime()
    return '{}-{:0>2}-{:0>2}'.format(tmp.tm_year, tmp.tm_mon, tmp.tm_mday)

print("Content-type: text/html\n\n")

date = getDateISO8601()
try:
    f = open('/var/log/MATE/websocket{}.log'.format(date), 'r')
    raw = f.read()
    f.close()

    raw = raw.replace('\n', '<br>')

    print(raw)
except FileNotFoundError as e:
    print(e)
