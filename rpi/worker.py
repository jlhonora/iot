#!/usr/bin/env python

import os
import node

import redis
from rq import Worker, Queue, Connection
from psycopg2.pool      import ThreadedConnectionPool

listen = ['high', 'default', 'low']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_conn = redis.from_url(redis_url)
pool = ThreadedConnectionPool(minconn = 1, maxconn = 10, dsn = "dbname=pgtest2db user=pgtest2user")

def process_data(json_data):
    dbconn = pool.getconn()
    print "Worker: " + str(json_data)
    result = node.Node.create_new_measurements(dbconn, json_data)
    pool.putconn(dbconn)
    return result

if __name__ == '__main__':
    with Connection(redis_conn):
        print "Setting up Redis"
        worker = Worker(map(Queue, listen))
        worker.work()
