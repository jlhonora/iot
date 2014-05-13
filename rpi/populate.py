#!/usr/bin/env python

import psycopg2
import datetime
import node
import json

def insert_node(cursor):
	identifier = 1000
	name = "Antu Node"
	sql = "INSERT INTO nodes(identifier, name, created_at) VALUES (%s, %s, %s)"
	cursor.execute(sql, (identifier, name, datetime.datetime.utcnow()))
	node_id = cursor.fetchone()[0]
	node = Node.get_by_identifier(identifier)
	assert node.id == node_id
	assert node.name == name
	print "Node pass"
	return node_id

def insert_sensor(cursor):
	sensor_type = 'counter'
	name = "Antu Counter"
	sql = "INSERT INTO sensors(stype, name, created_at, updated_at) VALUES (%s, %s, %s, %s)"
	cursor.execute(sql, (sensor_type, name, datetime.datetime.utcnow(), datetime.datetime.utcnow()))
	sensor_id = cursor.fetchone()[0]
	sensor = Sensor.get_by_id(sensor_id)
	assert sensor.id == sensor_id
	assert sensor.sensor_type == sensor_type
	assert sensor.name == name
	print "Sensor pass"
	return sensor_id

def insert_config(cursor, node_id, sensor_id):
	configs = [{'name': 'Battery', 'formula': {'0': int(1 << 8), '1': 1}}, {'name': 'Counter 32 bit', 'formula': {'2': int(1 << 24), '3': int(1 << 16), '4': int(1 << 8), '5': 1}}]
	sql = "INSERT INTO configurations(name, node_id, sensor_id, formula, created_at) VALUES (%s, %s, %s, %s, %s)"
	for config in configs:
		cursor.execute(sql, (config['name'], node_id, sensor_id, config['formula'], datetime.datetime.utcnow()))
		config_id = cursor.fetchone()[0]
		config = Config.get_by_id(config_id)
		assert config.id == config_id
		assert config.name == config['name']
		assert config.formula == json.dumps(config['formula'])
	print "Config pass"

if __name__ == "__main__":
	print "Populating DB"
	with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as conn:
		with conn.cursor() as cursor:
			node_id = insert_node(cursor)
			sensor_id = insert_sensor(cursor)
			insert_config(cursor, node_id, sensor_id)
		conn.close()
	print "Done"

