#!/usr/bin/env python

import json
import rq
from worker import redis_conn, process_data
from BaseHTTPServer     import HTTPServer, BaseHTTPRequestHandler
from SimpleHTTPServer   import SimpleHTTPRequestHandler
from redis              import Redis

class SimpleHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>OK</h1></body></html>")
 
    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Read the data
        content_len = int(self.headers.getheader('content-length'))
        post_body = self.rfile.read(content_len)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'response': 'ok'}))
        print "Body: " + str(post_body)
        self.queue_data(post_body)

    def queue_data(self, json_data):
        print "Queueing data"
        rq.Queue(connection=redis_conn).enqueue(process_data, str(json_data))
        print "Done queueing data"

def run():
    print "Running"
    # This is deprecated but I can't figure out
    # how to do it the right way

    HandlerClass = SimpleHandler
    ServerClass  = HTTPServer
    Protocol     = "HTTP/1.0"
    port = 8081
    server_address = ("localhost", port)

    HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

if __name__ == "__main__":
    run()
