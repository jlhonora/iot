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
            sql = "UPDATE configurations SET node_id = (%s), name = (%s), sensor_id=(%s), formula=(%s) WHERE id = (%s)"
            cursor.execute(sql, (self.node_id, self.name, self.sensor_id, json.dumps(self.formula), datetime.datetime.utcnow(), self.id))
        else:
            sql = "INSERT INTO configurations(node_id, name, sensor_id, formula, created_at) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.node_id, self.name, self.sensor_id, json.dumps(self.formula), datetime.datetime.utcnow()))

    def to_json(self):
        json = {}
        json['id'] = self.id
        json['name'] = self.name
        json['node_id'] = self.node_id
        json['sensor_id'] = self.sensor_id
        json['formula'] = self.formula
        json['created_at'] = self.created_at
        return json

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
            new_config.formula = json.loads(json_config['formula'])
        if 'created_at' in json_config:
            new_config.created_at = json_config['created_at']
        return new_config

    @staticmethod
    def get_by_id(cursor, config_id):
        # Query params always with %s, must pass a tuple
        cursor.execute("SELECT * FROM configurations WHERE id = (%s)", (config_id,))
        results = cursor.fetchall()
        if len(results) == 0:
            return None
        # Get last element
        result = results[-1]
        json_config = NodeConfig.tuple2json(result)
        # Query results are tuples
        return NodeConfig.init(json_config)

    @staticmethod
    def get_configs_by_node_id(cursor, node_id):
        cursor.execute("SELECT * FROM configurations WHERE node_id = (%s)", (node_id,))
        result = cursor.fetchall()
        configs = []
        for r in result:
            json_config = NodeConfig.tuple2json(r)
            configs = configs + [NodeConfig.init(json_config)]
        return configs

    @staticmethod
    def get_configs_by_sensor_id(cursor, sensor_id):
        result = cursor.execute("SELECT * FROM configurations WHERE sensor_id = (%s)", (sensor_id,))
        configs = []
        for r in result:
            configs = configs + [NodeConfig.init(r)]
        return configs

    @staticmethod
    def tuple2json(tup):
        json = {}
        json['id'] = tup[0]
        json['name'] = tup[1]
        json['node_id'] = tup[2]
        json['sensor_id'] = tup[3]
        json['formula'] = tup[4]
        return json
        
