#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

dc() {
   docker-compose -p test -f docker-compose-test.yml $*;
}

trap 'dc down; dc kill ; dc rm -f' EXIT

dc down || true
dc build
dc pull

dc up -d database
dc up -d elasticsearch

sleep 6  # sometimes DB creation is not ready yet

dc run --rm ppapi /app/docker-wait.sh

echo "Prepare some testdata for elastic to test API"

echo "Create normal empty database"
dc run --rm ppapi python manage.py migrate

echo "# load test data into database"
dc run --rm ppapi bash testdata/loadtestdata.sh parkeerscans || true

echo "start logstash to index data from database into elastic"

dc run --rm logstash /app/load-test-data.sh

# now we are ready to run some tests
dc run --rm ppapi python manage.py test

dc down
dc rm -f
