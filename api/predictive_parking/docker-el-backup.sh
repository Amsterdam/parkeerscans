#!/bin/bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x


docurl() {
	curl -s --trace-ascii -H "Content-Type: application/json" -f -XPUT $*
}

docurl http://elasticsearch:9200/_snapshot/backup -d '
{
  "type": "fs",
  "settings": {
      "location": "/tmp/backups" }
}'

docurl http://elasticsearch:9200/_snapshot/backup/scans?wait_for_completion=true -d '
{ "indices": "scans*" }'
