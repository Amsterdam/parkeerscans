#!/bin/bash

set -u   # crash on missing env variables
set -e   # stop on any error


curl -s --trace-ascii -f -XPUT http://elasticsearch:9200/_snapshot/backup -d '
{
  "type": "fs",
  "settings": {
      "location": "/tmp/backups" }
}'

curl -s --trace-ascii -f -XPUT http://elasticsearch:9200/_snapshot/backup/scans?wait_for_completion=true -d '
{ "indices": "scans*" }'
