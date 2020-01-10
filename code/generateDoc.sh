#!/bin/bash

# Generates documentation for all the Python code in CISSROV using pdoc3

cd ..
pdoc3 --html code -o docs --force
cd code
