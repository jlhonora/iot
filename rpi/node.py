#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import datetime
import json
import time
import string
import random

class Node:
	id = None
	identifier = None
	name = None
	created_at = None
	updated_at = None

	def __init__(self):
		self.created_at = datetime.datetime.utcnow()
		self.updated_at = self.created_at

	def save(self, cursor):
		if self.id is not None:
			sql = "UPDATE nodes SET name = (%s), updated_at=(%s) WHERE id = (%s)"
			cursor.execute(sql, (self.name, datetime.datetime.utcnow(), self.id))
		else:
			sql = "INSERT INTO nodes(identifier, name, created_at, updated_at) VALUES (%s, %s, %s, %s)"
			cursor.execute(sql, (self.identifier, self.name, datetime.datetime.utcnow(), datetime.datetime.utcnow()))

	def get_configs(self, cursor):
		return NodeConfig.get_configs_by_node_id(self.id, cursor)
		# return [{'formula': {'0': int(1 << 8), '1': 1}}, {'formula': {'2': int(1 << 24), '3': int(1 << 16), '4': int(1 << 8), '5': 1}}]

	def new_measurement(self, value, cursor, created_at = None):
		if created_at is None:
			created_at = datetime.datetime.utcnow()
		else:
			created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
		sql = "INSERT INTO measurements(sensor_id, value, created_at) VALUES (%s, %s, %s)"
		cursor.execute(sql, (int(self.id), value, created_at))

	@staticmethod
	def init(json_node):
		if json_node is None:
			return None
		new_node = Node()
		print "Json node: " + str(json_node)

		if 'id' in json_node:
			new_node.id = int(json_node['id'])
		if 'identifier' in json_node:
			new_node.identifier = json_node['identifier']
		if 'name' in json_node:
			new_node.name = json_node['name']
		if 'created_at' in json_node:
			new_node.created_at = json_node['created_at']
		else:
			new_node.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
		return new_node
	
	@staticmethod
	def name_generator(size=6, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	@staticmethod
	def get_by_identifier(cursor, node_identifier):
		# Query params always with %s, must pass a tuple
		cursor.execute("SELECT * FROM nodes WHERE identifier = (%s)", (node_identifier,))
		results = cursor.fetchall()
		# Get last element
		result = results[-1]
		# Query results are tuples
		json_node = {}
		json_node['id'] = result[0]
		json_node['identifier'] = result[1]
		json_node['name'] = result[2]
		json_node['created_at'] = result[3]
		return Node.init(json_node)

	@staticmethod
	def get_by_identifier_or_create(cursor, node_identifier):
		node = Node.get_by_identifier(cursor, node_identifier)
		if node is None:
			node = Node.init({'identifier': node_identifier})
			node.save()
		return node

	@staticmethod
	def create_new_measurements(dbconn, json_data):
		if json_data is None:
			return False
		if isinstance(json_data, str):
			json_data = json.loads(json_data)
		if 'payload' in json_data:
			return Node.process_payload(dbconn, json_data['payload'])
			
		return False
	
	@staticmethod
	def process_payload(dbconn, payload):
		dbconn.autocommit = True
		slots = payload.split(',')	
		node_identifier = slots[0]
		measurements = slots[1:]
		# The connection will remain open after this
		# The cursor is closed after this block
		with dbconn.cursor() as curs:
			node = Node.get_by_identifier_or_create(curs, node_identifier)
			if node is None:
				print "Node %s doesn't exist" % node_identifier
				return False
			else:
				print "Node %s: %s" % (node.identifier, node.name)
				configs = node.get_configs(curs)
				if configs is None:
					return False
				results = []
				for config in configs:
					values = []
					formula = config['formula']
					for key, value in config.iteritems():
						if int(key) < len(measurements):
							values = values + [int(measurements[int(key)]) * float(config[key])]
						else:
							break
					results = results + [sum(values)]
				print "Got results: ", results
				for result in results:
					node.new_measurement(result, curs)
				return True
		return False

