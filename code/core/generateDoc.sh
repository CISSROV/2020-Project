#!/bin/bash

loc="../../docs/core"

pdoc3 --html motor2020++.py -o $loc --force
pdoc3 --html motor2020.py -o $loc --force
pdoc3 --html server2020.py -o $loc --force
pdoc3 --html webSocketClient.py -o $loc --force