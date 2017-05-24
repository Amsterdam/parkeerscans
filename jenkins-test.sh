#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
   docker-compose -p -f docker-compose-test.yml test $*;
}
#

dc build
dc up -d database
dc up -d elasticsearch

sleep 15

source docker-wait.sh

# we prepare some testdata for elastic

# create normal database
python manage.py migrate

# load test data into database
bash testdata/loadtestdata.sh predictiveparking || true

# start logstash to index data from database into elastic
bash testdata/loadelastic.sh predictiveparking

# now we are ready to run some tests
python manage.py test

dc stop
dc rm -f
