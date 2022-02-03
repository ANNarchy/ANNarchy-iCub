#!/bin/bash

for speed in 10 50 100
do
    python3 joint_motion_control.py all $speed
done