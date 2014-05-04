#!/usr/bin/env python

import json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler

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
		print "Body: " + str(post_body)
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(json.dumps({'response': 'ok'}))

def run():
	HandlerClass = SimpleHandler
	ServerClass  = HTTPServer
	Protocol     = "HTTP/1.0"
	port = 8081
	server_address = ('127.0.0.1', port)

	HandlerClass.protocol_version = Protocol
	httpd = ServerClass(server_address, HandlerClass)

	sa = httpd.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()

# TODO: Change to __init__
run()
