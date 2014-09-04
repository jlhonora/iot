#!/usr/bin/env python
# Based on https://github.com/starlock/vino/wiki/API-Reference
# JLH Sep, 2014

import yaml
import json
import urllib
import urllib2

class Vine:
    username = None
    password = None
    credentials_file = 'vine_api_config.yml'

    def __init__(self):
        if self.username is None or self.password is None:
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
        req = urllib2.Request("https://api.vineapp.com/users/authenticate", urllib.urlencode(json_data))
        req.add_header('User-Agent', 'com.vine.iphone/1.0.5 (unknown, iPhone OS 5.1.1, iPhone, Scale/2.000000)')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'en, fr, de, ja, nl, it, es, pt, pt-PT, da, fi, nb, sv, ko, zh-Hans, zh-Hant, ru, pl, tr, uk, ar, hr, cs, el, he, ro, sk, th, id, ms, en-GB, ca, hu, vi, en-us;q=0.8')
        req.add_header('Accept-Encoding', 'gzip')
        try:
            response = urllib2.urlopen(req)
            print response.read()
            response.close()
            return True
        except Exception as e:
            print "Response failed"
            print str(e)
        return False

    def upload_video(self, filename):
        self.authenticate()
        
if __name__ == '__main__':
    api = Vine()
    print "Auth: " + str(api.authenticate())
