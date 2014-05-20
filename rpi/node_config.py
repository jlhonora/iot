# -*- coding: utf-8 -*-

import json
import datetime

class NodeConfig:
	id = None
	name = None
	node_id = None
	sensor_id = None
	formula = None
	created_at = None

	def __init__(self):
		self.created_at = datetime.datetime.utcnow()

	def save(self, cursor):
		if self.id is not None:
			sql = "UPDATE node_configs SET node_id = (%s), name = (%s), sensor_id=(%s), formula=(%s) WHERE id = (%s)"
			cursor.execute(sql, (self.node_id, self.name, self.sensor_id, self.formula, datetime.datetime.utcnow(), self.id))
		else:
			sql = "INSERT INTO node_configs(node_id, name, sensor_id, formula, created_at) VALUES (%s, %s, %s, %s, %s)"
			cursor.execute(sql, (self.node_id, self.name, self.sensor_id, self.formula, datetime.datetime.utcnow()))

	@staticmethod
	def init(json_config):
		if json_config is None:
			return None
		
		new_config = NodeConfig()

		if 'id' in json_config:
			new_config.id = json_config['id']
		if 'name' in json_config:
			new_config.name = json_config['name']
		if 'node_id' in json_config:
			new_config.node_id = json_config['node_id']
		if 'sensor_id' in json_config:
			new_config.sensor_id = json_config['sensor_id']
		if 'formula' in json_config:
			new_config.formula = json_config['formula']
		if 'created_at' in json_config:
			new_config.created_at = json_config['created_at']
		return new_config

	@staticmethod
	def get_by_id(cursor, config_id):
		# Query params always with %s, must pass a tuple
		cursor.execute("SELECT * FROM configurations WHERE id = (%s)", (config_id,))
		results = cursor.fetchall()
		# Get last element
		result = results[-1]
		# Query results are tuples
		json_config = {}
		json_config['id'] = result[0]
		json_config['name'] = result[1]
		json_config['node_id'] = result[2]
		json_config['sensor_id'] = result[3]
		json_config['formula'] = result[4]
		return NodeConfig.init(json_config)

	@staticmethod
	def get_configs_by_node_id(node_id, cursor):
		result = cursor.execute("SELECT * FROM node_configs WHERE node_id = (%s)", (node_id,))
		configs = []
		for r in result:
			configs = configs + [NodeConfig.init(r)]
		return configs

	@staticmethod
	def get_configs_by_sensor_id(sensor_id, cursor):
		result = cursor.execute("SELECT * FROM node_configs WHERE sensor_id = (%s)", (sensor_id,))
		configs = []
		for r in result:
			configs = configs + [NodeConfig.init(r)]
		return configs
