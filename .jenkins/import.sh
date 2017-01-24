#!/bin/bash

set -e
set -u

DIR="$(dirname $0)"

echo $0

dc() {
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}

trap 'dc kill ; dc rm -f' EXIT

echo "Do we have OS password?"
echo $PARKEERVAKKEN_OBJECTSTORE_PASSWORD

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc build --pull

dc up -d database

#dc run --rm tests

# load latest bag into database
echo "Load latest parkeervakken.."
#dc exec -T database update-table.sh parkeervakken parkeervakken bv predictiveparking
echo "Load latest wegdelen.."
#dc exec -T database update-table.sh basiskaart bgt_wegdeel bgt predictiveparking

echo "create scan api database"
# create the scan_database and reset elastic
dc run --rm importer docker-prepare.sh


echo "DONE! importing scans into database"

#echo "create hr dump"
## run the backup shizzle
#dc run --rm db-backup
#
#START_DATE="2016-01-01" END_DATE="2017-01-01" dc run --rm logstash
#
#dc run --rm el-backup
#
#echo "DONE! with everything! You are awesome! <3"
