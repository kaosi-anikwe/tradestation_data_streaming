#!/bin/bash

# Check if the process is running
if pgrep -f "python -u main.py" > /dev/null; then
    echo "Stopping the Python script..."
    pkill -f "python -u main.py"
    echo "Python script stopped."
else
    echo "Python script is not running."
fi
