#!/bin/bash

# Start the redis server to manage the queue
redis-server          &

# The worker that reads from the redis queue and processes
# the enqueued objects
python worker.py              &

# Receives HTTP requests for data and fills the queue
python api_manager.py &

# Reads from the serial port and sends messages to api_manager
python reader.py	&

# Sends a tweet with the ran distance 
python twitter_manager.py      &
