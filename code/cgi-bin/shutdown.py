#!/usr/bin/env python3.4
import os

print ("Content-type: text/html\n\n")

file = 'sudo /var/www/scripts/dataCollection.sh stop'
result = os.popen(file).read()

print('<h3>Shutting Down dataGetter.py</h3>')
print('<p>' + str(result) + '</p>')
print('<br>')
print('<a href=\'dataSheet.html\'>Link to Data Sheet</a>')
