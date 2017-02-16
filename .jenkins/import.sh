#!/bin/bash

set -e
set -u

DIR="$(dirname $0)"

echo $0

dc() {
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}

dc stop
dc rm -f

#trap 'dc kill ; dc rm -f' EXIT

echo "Do we have OS password?"
echo $PARKEERVAKKEN_OBJECTSTORE_PASSWORD

echo "Testing import? if (yes)"
echo $TESTING

# get the latest and greatest
dc pull


dc up -d database
dc up -d elasticsearch

sleep 10
#dc run --rm tests
# and download scans zipfiles and rars

echo "IF ELK5 fails to start / unknown host.. then RUN 'sysctl -w vm.max_map_count=262144'"
dc run importer dig elasticsearch

echo "create scan api database"
# create the scan_database
dc run importer ./docker-prepare.sh
#
echo "Load latest parkeervakken.."
dc exec -T database update-table.sh parkeervakken parkeervakken bv predictiveparking
echo "Load latest wegdelen.."
dc exec -T database update-table.sh basiskaart bgt_wegdeel bgt predictiveparking
echo "Load buurt / buurtcombinatie"
dc exec -T database update-table.sh bag bag_buurt public predictiveparking

echo "loading the unzipped scans into database"
dc run csvimporter app


echo "create wegdelen / buurten and complete the scans data"
dc run importer ./docker-import.sh

# we have to chunk the importing otherwise the database
# will take minutes to get data logstash needs
if [ $TESTING = "yes" ] ;
then
  START_DATE="2016-10-01" END_DATE="2016-11-01" dc run logstash
else
  START_DATE="2016-01-01" END_DATE="2016-02-01" dc run logstash
  START_DATE="2016-02-01" END_DATE="2016-03-01" dc run logstash
  START_DATE="2016-03-01" END_DATE="2016-04-01" dc run logstash
  START_DATE="2016-04-01" END_DATE="2016-05-01" dc run logstash
  START_DATE="2016-05-01" END_DATE="2016-06-01" dc run logstash
  START_DATE="2016-06-01" END_DATE="2016-07-01" dc run logstash
  START_DATE="2016-07-01" END_DATE="2016-08-01" dc run logstash
  START_DATE="2016-09-01" END_DATE="2016-10-01" dc run logstash
  START_DATE="2016-10-01" END_DATE="2016-11-01" dc run logstash
  START_DATE="2016-11-01" END_DATE="2016-12-01" dc run logstash
  START_DATE="2016-12-01" END_DATE="2017-01-01" dc run logstash
fi

echo "DONE! importing scans into database"

echo "create scan db dump"
# run the backup shizzle
dc up db-backup
#
#
dc up el-backup
#
echo "DONE! with import. You are awesome! <3"
dc stop
