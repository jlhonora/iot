#!/bin/bash

# Start the redis server to manage the queue
redis-server redis.conf &

# Receives HTTP requests for data and fills the queue
python -u api_manager.py &

# Reads from the serial port and sends messages to api_manager
python -u reader.py	&

# Sends a tweet with the ran distance 
python -u twitter_manager.py &

# The worker that reads from the redis queue and processes
# the enqueued objects
python -u worker.py &

# Creates videos continuously
sudo python -u camera_director.py &
