#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

dc() {
   docker-compose -p test -f docker-compose-test.yml $*;
}

dc build

dc up -d database
dc up -d elasticsearch

sleep 5  # sometimes DB creation is not ready yet

dc run ppapi /app/docker-wait.sh

echo "Prepare some testdata for elastic to test API"

echo "Create normal empty database"
dc run --rm ppapi python manage.py migrate

echo "# load test data into database"
dc run --rm ppapi bash testdata/loadtestdata.sh predictiveparking || true

echo "start logstash to index data from database into elastic"

dc run logstash /app/load-test-data.sh
sleep 2  #  wait for elastic to be ready.

# now we are ready to run some tests
dc run --rm ppapi python manage.py test

dc stop
dc rm -f
