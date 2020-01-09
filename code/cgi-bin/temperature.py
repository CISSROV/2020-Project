#!/usr/bin/env python3.4
'''
Author: Jonathan Rotter

Uses tempSensor.py located
in `/var/www/scripts` to fetch
the temperature from the
external thermometer.
'''

if __name__ == '__main__':
    # Add a location for python to search for modules to import
    from sys import path
    path.append('/var/www/scripts')

    # Import tempSensor module located in "/var/www/scripts"
    try:
        import tempSensor
    except ModuleNotFoundError:
        raise ModuleNotFoundError("tempSensor.py is missing in /var/www/scripts")

    # Print header specifying file type
    print("Content-type: text/html\n\n")

    # Open and read the html file
    f = open('temperature.html')
    txt = f.read()
    f.close()

    # Get the temperature using the tempSensor module
    data = tempSensor.getTemp()

    # Put the temperature into the html file where the comment "<!-- tag -->" is
    txt = txt.replace('<!-- tag -->', str(data))

    # Print final html
    print(txt)
