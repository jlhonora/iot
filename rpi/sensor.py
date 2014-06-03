#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import datetime
import json
import time
import string
import random

class Sensor:
    id = None
    sensor_type = 'default'
    name = None
    created_at = None
    updated_at = None

    def __init__(self):
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at 

    def save(self, cursor):
        if self.id is not None:
            sql = "UPDATE sensors SET name = (%s), stype = (%s), updated_at = (%s) WHERE id = (%s)"
            cursor.execute(sql, (self.name, self.sensor_type, datetime.datetime.utcnow(), self.id))
        else:
            sql = "INSERT INTO sensors(stype, name, created_at, updated_at) VALUES (%s, %s, %s, %s)"
            timestamp = datetime.datetime.now()
            cursor.execute(sql, (self.sensor_type, self.name, timestamp, timestamp))

    def get_configs(self, cursor):
        return SensorConfig.get_configs_by_sensor_id(self.id, cursor)

    def new_measurement(self, cursor, value, created_at = None):
        if created_at is None:
            created_at = datetime.datetime.utcnow()
        else:
            created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO measurements(sensor_id, value, created_at) VALUES (%s, %s, %s)"
        cursor.execute(sql, (int(self.id), value, created_at))
        self.save(cursor)

    @staticmethod
    def init(json_sensor):
        if json_sensor is None:
            return None
        new_sensor = Sensor()

        if 'id' in json_sensor:
            new_sensor.id = int(json_sensor['id'])
        if 'sensor_type' in json_sensor:
            new_sensor.sensor_type = json_sensor['sensor_type']
        if 'name' in json_sensor:
            new_sensor.name = json_sensor['name']
        if 'created_at' in json_sensor:
            new_sensor.created_at = json_sensor['created_at']
        else:
            new_sensor.created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        if 'updated_at' in json_sensor:
            new_sensor.updated_at = json_sensor['updated_at']
        else:
            new_sensor.updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        return new_sensor
    
    @staticmethod
    def name_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def get_by_id(cursor, sensor_id):
        # Query params always with %s, must pass a tuple
        cursor.execute("SELECT * FROM sensors WHERE id = (%s)", (sensor_id,))
        results = cursor.fetchall()
        # Get last element
        result = results[-1]
        # Query results are tuples
        json_sensor = Sensor.tuple2json(result)
        return Sensor.init(json_sensor)

    @staticmethod
    def get_by_id_or_create(cursor, sensor_id):
        sensor = Sensor.get_by_identifier(cursor, sensor_id)
        if sensor is None:
            sensor = Sensor.init({'id': sensor_id})
            sensor.save()
        return sensor

    @staticmethod
    def get_by_name(cursor, sensor_name):
        cursor.execute("SELECT * FROM sensors WHERE name = (%s)", (sensor_name,))
        results = cursor.fetchall()
        # Get last element
        result = results[-1]
        # Query results are tuples
        json_sensor = Sensor.tuple2json(result)
        return Sensor.init(json_sensor)

    @staticmethod
    def tuple2json(tup):
        json = {}
        json['id'] = tup[0]
        json['sensor_type'] = tup[1]
        json['name'] = tup[2]
        json['created_at'] = tup[3]
        json['updated_at'] = tup[4]
        return json
        
