#!/usr/bin/env python

import psycopg2
import datetime
import node
import sensor
import node_config as config
import json

def insert_node(cursor):
	identifier = str(1000)
	name = "Antu Node"
	sql = "INSERT INTO nodes(identifier, name, created_at) VALUES (%s, %s, %s) RETURNING *"
	cursor.execute(sql, (identifier, name, datetime.datetime.utcnow()))
	node_id = cursor.fetchone()[0]
	print "Got id: " + str(node_id)
	node_obj = node.Node.get_by_identifier(cursor, identifier)
	assert int(node_obj.id) == int(node_id)
	assert str(node_obj.name) == str(name)
	print "Node pass"
	return node_id

def insert_sensor(cursor):
	sensor_type = 'counter'
	name = "Antu Counter"
	sql = "INSERT INTO sensors(stype, name, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING *"
	cursor.execute(sql, (sensor_type, name, datetime.datetime.utcnow(), datetime.datetime.utcnow()))
	sensor_id = cursor.fetchone()[0]
	sensor_obj = sensor.Sensor.get_by_id(cursor, sensor_id)
	assert sensor_obj.id == sensor_id
	assert sensor_obj.sensor_type == sensor_type
	assert sensor_obj.name == name
	print "Sensor pass"
	return sensor_id

def insert_config(cursor, node_id, sensor_id):
	configs = [{'name': 'Battery', 'formula': {'0': int(1 << 8), '1': 1}}, {'name': 'Counter 32 bit', 'formula': {'2': int(1 << 24), '3': int(1 << 16), '4': int(1 << 8), '5': 1}}]
	sql = "INSERT INTO configurations(name, node_id, sensor_id, formula, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING *"
	for elem in configs:
		cursor.execute(sql, (elem['name'], node_id, sensor_id, str(elem['formula']), datetime.datetime.utcnow()))
		config_id = cursor.fetchone()[0]
		config_obj = config.NodeConfig.get_by_id(cursor, config_id)
		assert config_obj.id == config_id
		assert config_obj.name == elem['name']
		assert str(config_obj.formula) == str(elem['formula'])
	print "Config pass"

if __name__ == "__main__":
	print "Populating DB"
	with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as conn:
		conn.autocommit = True
		with conn.cursor() as cursor:
			node_id = insert_node(cursor)
			sensor_id = insert_sensor(cursor)
			insert_config(cursor, node_id, sensor_id)
	print "Done"

