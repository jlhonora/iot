#!/usr/bin/env python
# Based on https://github.com/starlock/vino/wiki/API-Reference
# JLH Sep, 2014

import yaml
import json
import poster
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

import urllib
import urllib2

import requests

class Vine:
    username = None
    password = None
    credentials_file = 'vine_api_config.yml'
    key = None

    def __init__(self, key = None):
        self.key = key
        if self.username is None or self.password is None or self.key is None:
            self.init_with_file()

    def init_with_file(self, filename = credentials_file):
        with open(filename, 'r') as f:
            doc = yaml.load(f)
            self.username = doc['username']
            self.password = doc['password']

    def authenticate(self):
        if self.username is None or self.password is None:
            return False
        json_data = {'username':self.username,'password': self.password}
        headers = {}
        headers['User-Agent'] = 'iphone/1.3.1 (iPad; iOS 6.1.3; Scale/1.00)'
        headers['Accept'] = '*/*'
        headers['Accept-Language'] = 'en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5'
        headers['Accept-Encoding'] = 'gzip'
        print headers
        try:
            req = requests.post("https://api.vineapp.com/users/authenticate", data = json_data, headers = headers)
            print req.text
            response_json = json.loads(req.text)
            self.key = response_json['data']['key']
            return True
        except Exception as e:
            print "Response failed"
            print str(e)
        return False

    def upload_video(self, filename):
        if self.key is None:
            self.authenticate()
        files = {"file": (filename, open(filename, "rb"), 'video/mp4', {'Expires': '0'})}
        headers = {}
        headers['Host'] = 'media.vineapp.com'
        headers['Proxy-Connection'] = 'keep-alive'
        headers['Content-Type'] = 'video/mp4'
        headers['X-Vine-Client'] = 'ios/1.3.1'
        headers['Accept-Language'] = 'en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5'
        headers['Accept'] = '*/*'
        headers['Vine-Session-Id'] = str(self.key)
        headers['Accept-Encoding'] = 'gzip, deflate'
        headers['Connection'] = 'keep-alive'
        headers['User-Agent'] = 'iphone/1.3.1 (iPad; iOS 6.1.3; Scale/1.00)'
        try:
            print "Making request"
            req = requests.put("https://media.vineapp.com/upload/videos/1.3.1.mp4", headers = headers, files = files)
            print "Parsing response"
            print str(req.json())
            response.close()
            return True
        except Exception as e:
            print "Response failed"
            print str(e)
        return False
        
if __name__ == '__main__':
    api = Vine()
    print "Auth: " + str(api.authenticate())
    api.upload_video('video.mp4')
