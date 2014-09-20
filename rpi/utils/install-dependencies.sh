#!/bin/bash

sudo apt-get -y install redis-server postgresql libpq-dev python-setuptools
sudo easy_install pip

sudo pip install pyserial rq psycopg2 pyyaml python-twitter schedule google-api-python-client
