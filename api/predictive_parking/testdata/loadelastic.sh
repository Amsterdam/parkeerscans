# load database into elastic search.
# for local test environment

set -e
set -u

DB=$1

if [ -z "$1" ]
then
      echo "No database name supplied using test_predictivepakring"
      DB="test_predictiveparking"
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

curl -s -v -f -XPUT http://elasticsearch:9200/_template/scan -d '
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

dc run -e "DB=$DB" -e "TABLE=metingen_scan" --rm logstash logstash -f readdb.conf
