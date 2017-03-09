#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

# prepare elastic templates for scan documents
# we need to put in manual elk point

# wait for elastic
#while ! nc -z elasticsearch 9200
#do
# 	echo "Waiting for elastic..."
# 	sleep 1.5
#done
export ELKHOST='http://es01-acc.datapunt.amsterdam.nl'


# curl -s -v -f -XDELETE http://${ELKHOST:-elasticsearch}:9200/_template/scan || echo 'OK'
curl -s -v -f -XPUT http://${ELKHOST:-elasticsearch}:9200/_template/scan -d '
{
  "template": "scans-*",
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "scan": {
      "properties": {
        "geo": {
          "type": "geo_point"
        }
      }
    }
  }
}'

echo "Indexing start: $START_DATE"
echo "Indexing   end: $END_DATE"


logstash -f readdb.conf --pipeline.workers 3
