#!/bin/bash

python3.4 -c "print('Content-type: text/html\n\n')"
python3.4 -c "print('<h1>yay</h1>')"
echo '<p>test</p>'

cd /var/www/scripts

echo $?
