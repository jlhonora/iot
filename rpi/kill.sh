#!/bin/bash

# Kill python processes
echo "Terminating python processes"
sudo killall python

# Kill redis
REDIS_PROC=`ps aux | grep redis | grep -v grep | awk -F ' ' '{print $2}' | tr -d ' '`

if [ `echo $REDIS_PROC | wc -c` -gt 1 ]
then
	echo "Terminating Redis with process $REDIS_PROC"
	sudo kill -s TERM $REDIS_PROC
else
	echo "Redis not running"
fi
