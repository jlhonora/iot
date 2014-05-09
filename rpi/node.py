#!/usr/bin/env python

import psycopg2
import datetime
import json

class Node:
	id = None
	name = None
	created_at = None

	def __init__(self):
		created_at = str(datetime.datetime.now());

	def save(self, cursor):
		if cursor is None:
			return False
		if self.id is not None:
			cursor.execute("UPDATE sensors SET name = (%s) WHERE id = (%s)", (self.name, self.id))

	@staticmethod
	def init(json_node):
		if json_node is None:
			return None
		new_node = Node()
		new_node.id = json_node['id']
		if 'name' in json_node:
			new_node.name = json_node['name']
		if 'created_at' in json_node:
			new_node.created_at = json_node['created_at']
		return new_node

	@staticmethod
	def get_by_id(cursor, node_id):
		# Query params always with %s, must pass a tuple
		result = cursor.execute("SELECT * FROM nodes WHERE id = (%s)", (node_id,))
		return Node.init(result)

	@staticmethod
	def get_by_id_or_create(cursor, node_id):
		node = Node.get_by_id(cursor, node_id)
		if node is None:
			node = Node.init({'id': node_id})
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
		slots = payload.split(',')	
		node_id = slots[0]
		measurements = slots[1:]
		# The connection will remain open after this
		# The cursor is closed after this block
		with dbconn.cursor() as curs:
			node = Node.get_by_id_or_create(curs, node_id)
			if node is None:
				print "Node %s doesn't exist" % node_id
				return False
			else:
				print "Got node %s: %s" % (node.id, node.name)
				return True
		return False

