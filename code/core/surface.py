import webSocketClient
import time

def f():
    return 'Hello World! ' + time.ctime()

webSocketClient.start('surface', f)
