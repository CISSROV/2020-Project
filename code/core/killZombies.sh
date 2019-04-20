#!/bin/bash

for i in $(pgrep -f "python hydrogen"); do
  kill -9 $i
done
