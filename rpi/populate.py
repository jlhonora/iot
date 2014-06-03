#!/usr/bin/env python

import psycopg2
import datetime
import node
import sensor
import node_config as config
import json

def insert_node(cursor, identifier, name):
    sql = "INSERT INTO nodes(identifier, name, created_at) VALUES (%s, %s, %s) RETURNING *"
    cursor.execute(sql, (identifier, name, datetime.datetime.utcnow()))
    node_id = cursor.fetchone()[0]
    print "Got id: " + str(node_id)
    node_obj = node.Node.get_by_identifier(cursor, identifier)
    assert int(node_obj.id) == int(node_id)
    assert str(node_obj.name) == str(name)
    print "Node pass"
    return node_id

def insert_sensor(cursor, name, sensor_type = 'default'):
    sql = "INSERT INTO sensors(stype, name, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING *"
    cursor.execute(sql, (sensor_type, name, datetime.datetime.utcnow(), datetime.datetime.utcnow()))
    sensor_id = cursor.fetchone()[0]
    sensor_obj = sensor.Sensor.get_by_id(cursor, sensor_id)
    assert sensor_obj.id == sensor_id
    assert sensor_obj.sensor_type == sensor_type
    assert sensor_obj.name == name
    print "Sensor pass"
    return sensor_id

def insert_config(cursor, node_id, sensor_id, cfg):
    sql = "INSERT INTO configurations(name, node_id, sensor_id, formula, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING *"
    cursor.execute(sql, (cfg['name'], node_id, sensor_id, json.dumps(cfg['formula']), datetime.datetime.utcnow()))
    config_id = cursor.fetchone()[0]
    config_obj = config.NodeConfig.get_by_id(cursor, config_id)
    assert config_obj.id == config_id
    assert config_obj.name == cfg['name']
    assert json.dumps(config_obj.formula) == json.dumps(cfg['formula'])
    print "Config pass"

if __name__ == "__main__":
    print "Populating DB"
    with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # Antu node
            node_id = insert_node(cursor, str(1035), "Antu Node")
            # Formulas for batteries (10-bit ADC) is (num / 2^precision) * voltage * voltage_div
            # In this case that is (num / 1024) * 3.3 * 2
            configs = [{'name': 'Battery', 'formula': {'8': "x * 0.006445"}}, {'name': 'Counter 32 bit', 'formula': {'5': "x * 65536", '3': "x"}}, {'name': 'Temp', 'formula': {'7': "(x - 5500.0) / 100.0"}}]
            sensor_id = insert_sensor(cursor, "Battery")
            insert_config(cursor, node_id, sensor_id, configs[0])
            sensor_id = insert_sensor(cursor, "Antu Counter", "counter")
            insert_config(cursor, node_id, sensor_id, configs[1])
            sensor_id = insert_sensor(cursor, "Antu Temp", "default")
            insert_config(cursor, node_id, sensor_id, configs[2])

            # Main node
            node_id = insert_node(cursor, str(1), "Master Node")
            configs = [{'name': 'Battery', 'formula': {'8': "x * 0.006445"}}]
            sensor_id = insert_sensor(cursor, "Main Battery")
            insert_config(cursor, node_id, sensor_id, configs[0])
    print "Done"

