#!/bin/bash

make upload
sleep 2s
python3 validate_dist.py
