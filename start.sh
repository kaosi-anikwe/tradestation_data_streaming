#!/bin/bash

# Change directory to the location of your Python script (if needed)
cd /home/kaosi/tradestation_data_streaming

# Activate venv
source env/bin/activate

# Start your Python script with nohup in the background
nohup python -u main.py >> tradestation.log 2>&1 &

echo "Python script started in the background."
