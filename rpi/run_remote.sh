#!/bin/bash
user_host=$1
ssh -n -f $user_host "sh -c 'cd /home/pi/iot/rpi; nohup ./run.sh > /var/log/iot/iot.log 2>&1 &'"
