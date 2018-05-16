# Load test database ~1000 scans into elastic search.

set -e
set -u
set -x

while ! ncat --send-only elasticsearch 9200 < /dev/null
do
 	echo "Waiting for elastic..."
 	sleep 1.5
done

curl -s -v -f -XDELETE http://elasticsearch:9200/_template/scan || echo 'OK'

curl -H "Content-Type: application/json" -s --trace-ascii -s -v -f -XPUT http://elasticsearch:9200/_template/scan -d '
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

DB=predictiveparking TABLE=metingen_scan logstash -f readdb.conf
