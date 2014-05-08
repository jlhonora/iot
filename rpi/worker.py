#!/usr/bin/env python

import psycopg2
import node

def process_data(json_data):
	print "Worker: " + str(json_data)
	return node.Node.create_new_measurements(json_data)

#def setupdb():
#	conn = psycopg2.connect("dbname=pgtest2db user=pgtest2user")
#	return True
	
