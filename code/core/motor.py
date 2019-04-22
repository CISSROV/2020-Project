import webSocketClient

def f(arg):
    print('msg:', arg)

webSocketClient.start('motor', f)
