#!/usr/bin/env bash

# load database into elastic search.
# for local test environment

set -e
set -u
set -x

DB=$1

if [ -z "$1" ]
then
      echo "No database name supplied using test_predictivepakring"
      DB="test_parkeerscans"
fi


dc() {
   docker-compose -p test $*;
}

dc up -d elasticsearch

while ! nc -z elasticsearch 9200
do
 	echo "Waiting for elastic..."
 	sleep 1.5
done

curl -H "Content-Type: application/json" -s  --trace-ascii -f -PUT http://elasticsearch:9200/_template/scan -d '
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

dc run -e "DB=$DB" -e "TABLE=metingen_scan" --rm logstash logstash -f readdb.conf
