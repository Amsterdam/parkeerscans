#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

max_workers=2

# prepare elastic templates for scan documents
# we need to put in manual elk point

while ! ncat --send-only elasticsearch 9200 < /dev/null
do
 	echo "Waiting for elastic..."
 	sleep 1.5
done


# export ELKHOST='http://es01-acc.datapunt.amsterdam.nl'


curl -s -v -f -XDELETE http://${ELKHOST:-elasticsearch}:9200/_template/scan || echo 'OK'

curl -H "Content-Type: application/json" -s --trace-ascii -f -PUT http://${ELKHOST:-elasticsearch}:9200/_template/scan -d '
{
  "index_patterns": ["scans-*"],
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

tablenames='/app/data/tables.txt'

export DB=predictiveparking

# while read tablename; do
# 	echo $tablename
# 	TABLE=$tablename logstash -f readdb.conf --pipeline.workers 4
# done < $tablenames

# run max_workers logstash instances.
< $tablenames xargs -P $max_workers -n 1 -I tablename env TABLE=tablename logstash -f readdb.conf --pipeline.workers 4 --path.data /tmp/tablename
