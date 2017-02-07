#!/bin/bash

set -e
set -u

DIR="$(dirname $0)"

echo $0

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*;
}

dc stop
dc rm -f

trap 'dc kill ; dc rm -f' EXIT

echo "Do we have OS password?"
echo $PARKEERVAKKEN_OBJECTSTORE_PASSWORD

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

# get the latest and greatest
dc pull


dc up -d database
dc up -d elasticsearch

sleep 10
#dc run --rm tests
# and download scans zipfiles and rars

echo "IF ELK5 fails to start / unknown host.. then RUN 'sysctl -w vm.max_map_count=262144'"
dc run importer dig elasticsearch

dc run importer ./docker-prepare.sh

# load latest bag into database
echo "Load latest parkeervakken.."
dc exec -T database update-table.sh parkeervakken parkeervakken bv predictiveparking
echo "Load latest wegdelen.."
dc exec -T database update-table.sh basiskaart bgt_wegdeel bgt predictiveparking
echo "Load buurt / buurtcombinatie"
dc exec -T database update-table.sh bag bag_buurt public predictiveparking

echo "create scan api database"
# create the scan_database

echo "loading the unzipped scans into database"
# dc run csvimporter app

# we have to chunk the importing otherwise the database
# will take minutes to get data logstash needs
START_DATE="2016-01-01" END_DATE="2016-02-01" dc run logstash
START_DATE="2016-02-01" END_DATE="2016-03-01" dc run logstash
#START_DATE="2016-03-01" END_DATE="2016-04-01" dc run logstash
#START_DATE="2016-04-01" END_DATE="2016-05-01" dc run logstash
#START_DATE="2016-05-01" END_DATE="2016-06-01" dc run logstash
#START_DATE="2016-06-01" END_DATE="2016-07-01" dc run logstash
#START_DATE="2016-07-01" END_DATE="2016-08-01" dc run logstash
#START_DATE="2016-09-01" END_DATE="2016-10-01" dc run logstash
#START_DATE="2016-10-01" END_DATE="2016-11-01" dc run logstash
#START_DATE="2016-11-01" END_DATE="2016-12-01" dc run logstash
#START_DATE="2016-12-01" END_DATE="2017-01-01" dc run logstash

echo "DONE! importing scans into database"

echo "create scan db dump"
# run the backup shizzle
dc run --rm db-backup
#
#
dc run --rm el-backup
#
echo "DONE! with everything! You are awesome! <3"
