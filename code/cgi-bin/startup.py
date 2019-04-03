#!/usr/bin/env python3.4
import os

print ("Content-type: text/html\n\n")

file = '/var/www/scripts/startDataCollection.sh'
result = os.popen(file).read()

print('<h3>Starting Up dataGetter.py</h3>')
print('<p>' + str(result) + '</p>')
print('<br>')
print('<a href=\'dataSheet.html\'>Link to Data Sheet</a>')
