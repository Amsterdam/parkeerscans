#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # log commands

#dc() {
#   docker-compose -p test $*;
#}
#
#dc up -d database
#dc up -d elasticsearch
#
echo "is this started? docker-compose -p test up database elasticsearch"
source docker-wait.sh

sleep 15
# we prepare some testdata for elastic

# create normal database
python manage.py migrate

echo "installed postgres client? psql?"
# load test data into database
bash testdata/loadtestdata.sh predictiveparking || true

# start logstash to index data from database into elastic
bash testdata/loadelastic.sh predictiveparking

# now we are ready to run some tests
python manage.py test

#dc stop
#dc rm -f
