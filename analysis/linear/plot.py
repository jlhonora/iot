#!/usr/bin/env python

import pylab
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

x = []
y = []

f = open('input_diff_time.txt')
# f = open('input_linear_time.txt')

while True:
	line = f.readline()
	if (f is not None) and (' ' in line):
		[xx, yy] = line.strip().split(' ')
		x = x + [datetime.datetime.strptime(xx, "%Y-%m-%dT%H:%M:%S")]
		y = y + [int(yy)]
	else:
		break

fig, ax = plt.subplots()
ax.plot_date(x, y, '-')
ax.fmt_data = DateFormatter('%H:%M:%S')
fig.autofmt_xdate()

plt.show()
