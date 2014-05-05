#!/usr/bin/env python

import datetime

starting_time = datetime.datetime(year=2014, month=05, day=04, hour=20, minute=30)

f = open('input_diff.txt', 'r')
period = 12

squeeze_factor = 5

line = f.readline()
last_count = 0

while line != None:
	count = 0
	for i in range(squeeze_factor):
		line = f.readline()
		count = count + int(line.split(' ')[1].strip())

	print str(starting_time.date()) + "T" + str(starting_time.time()) + " " + str(count)
	starting_time = starting_time + datetime.timedelta(seconds = period * squeeze_factor)
