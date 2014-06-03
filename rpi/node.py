#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import datetime
import json
import time
import string
import random
import node_config as config
import sensor
import parser
from math import *

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
        return config.NodeConfig.get_configs_by_node_id(cursor, self.id)
        # return [{'formula': {'0': int(1 << 8), '1': 1}}, {'formula': {'2': int(1 << 24), '3': int(1 << 16), '4': int(1 << 8), '5': 1}}]

    @staticmethod
    def init(json_node):
        if json_node is None:
            return None
        new_node = Node()

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
        if len(results) == 0:
            return None
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
            node.save(cursor)
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
        if payload is None or len(payload) == 0:
            print "Invalid payload" 
            return True
        if payload[0] == '$':
            payload = payload[1:]
        slots = payload.split(',')  
        node_identifier = slots[0]
        measurements = slots[1:]
        # The connection will remain open after this
        # The cursor is closed after this block
        with dbconn.cursor() as cursor:
            node = Node.get_by_identifier_or_create(cursor, node_identifier)
            if node is None:
                print "Node %s doesn't exist" % node_identifier
                return False
            else:
                print "Node %s: %s" % (node.identifier, node.name)
                configs = node.get_configs(cursor)
                if configs is None:
                    return False
                results = []
                for cfg in configs:
                    values = []
                    formula = cfg.formula
                    if formula is None:
                        continue
                    if isinstance(formula, str):
                        formula = json.loads(formula)
                    for key, value in formula.iteritems():
                        if int(key) < len(measurements):
                            x = int(measurements[int(key)])
                            f = formula[key]
                            code = parser.expr(f).compile()
                            values = values + [eval(code)]
                        else:
                            break
                    result = sum(values)
                    sens = sensor.Sensor.get_by_id(cursor, cfg.sensor_id)
                    if sens is None:
                        continue
                    sens.new_measurement(cursor, result)
                    results = results + [result]
                print "Got results: ", results
                return True
        return False

