#!/bin/bash

set -e
set -u

DIR="$(dirname $0)"

echo $0

echo "Do we have OS password?"
echo $PARKEERVAKKEN_OBJECTSTORE_PASSWORD
#
echo "Testing import? if (yes)"
echo $TESTING

echo "Run elastic import? if (yes)"
echo $RUNELASTIC



dc() {
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}

# so we can delete named volumes
dc stop
dc rm -f -v

trap 'dc kill ; dc rm -f -v' EXIT

if [ $TESTING != "yes" ]
then
	docker volume rm pp_data-volume || true
fi

docker volume rm pp_unzip-volume || true

#
## get the latest and greatest

dc pull

dc rm -f importer
dc rm -f csvimporter

dc build
#
dc up -d database
#


echo "create scan api database"
dc run --rm importer ./docker-migrate.sh
echo "download latest files.."
dc run --rm importer ./docker-prepare-csvdata.sh
#
dc exec -T database pg_restore -c -O -U predictiveparking -d predictiveparking /app/data/mvp.dump
echo "Load latest parkeervakken.."
dc exec -T database update-table.sh parkeervakken parkeervakken bv predictiveparking
echo "Load latest wegdelen.."

# foutparkeerders / scans niet in vakken
dc exec -T database update-table.sh basiskaart BGT_OWGL_verkeerseiland bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_OWGL_berm bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_OTRN_open_verharding bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_OTRN_transitie bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_WGL_fietspad bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_WGL_voetgangersgebied bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_WGL_voetpad bgt predictiveparking

# scans op wegen en vakken
dc exec -T database update-table.sh basiskaart BGT_WGL_parkeervlak bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_lokale_weg bgt predictiveparking
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_regionale_weg bgt predictiveparking
#
#echo "Load buurt / buurtcombinatie"
dc exec -T database update-table.sh bag bag_buurt public predictiveparking
#
#
#echo "create wegdelen / buurten and complete the scans data"
dc run --rm importer ./docker-wegdelen.sh
#
echo "loading the unzipped scans into database, add wegdelen / pv to scans"

dc run --rm csvimporter app

# crate table list for logstash / scan count stats on wegdelen / vakken
dc run --rm importer ./docker-scanstats.sh

echo "DONE! importing scans into database"

echo "create scan db dump"
dc up -d elasticsearch

# run the DB backup shizzle
dc up db-backup

# dc up db-backup-scans

#
if [ $RUNELASTIC == "yes" ]
then

	dc run --rm logstash
	dc up el-backup
fi

#

echo "DONE! with scan data import. You are awesome! <3"
dc stop
