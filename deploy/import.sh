#!/bin/bash

set -e
set -u
set -x

DIR="$(dirname $0)"

echo $0

echo "Is there some space?"

df -h

echo "Do we have OS password?"
echo $PARKEERVAKKEN_OBJECTSTORE_PASSWORD
#
echo "Testing import? if (yes)"
echo $TESTING
echo "DO we have a startdate?"
echo $STARTDATE

dc() {
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}

# so we can delete named volumes
dc down --remove-orphans

## get the latest and greatest
dc pull

# Elastic needs to run afterwards..
# trap 'dc kill ; dc rm -f -v' EXIT

if [ $TESTING != "yes" ]
then
	docker volume rm pp_data-volume || true
fi

docker volume rm pp_databasevolume || true
docker volume rm pp_unzip-volume || true

#

dc rm -f importer
dc rm -f csvimporter

dc build
#
dc up -d database
#

dc run --rm importer ./docker-wait.sh

echo "create scan api database"
dc run --rm importer ./docker-migrate.sh

echo "download latest files.."
dc run --rm importer ./docker-prepare-csvdata.sh
#
echo "Load latest parkeervakken.."
dc exec -T database update-table.sh parkeervakken parkeervakken bv parkeerscans
echo "Load latest wegdelen.."

# foutparkeerders / scans niet in vakken
dc exec -T database update-table.sh basiskaart BGT_OWGL_verkeerseiland bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_OWGL_berm bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_OTRN_open_verharding bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_OTRN_transitie bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_WGL_fietspad bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_WGL_voetgangersgebied bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_WGL_voetpad bgt parkeerscans

# scans op wegen en vakken
dc exec -T database update-table.sh basiskaart BGT_WGL_parkeervlak bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_lokale_weg bgt parkeerscans
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_regionale_weg bgt parkeerscans

#echo "Load buurt / buurtcombinatie"
dc exec -T database update-table.sh bag bag_buurt public parkeerscans


# echo "create wegdelen / buurten and complete the scans data"
dc run --rm importer ./docker-wegdelen.sh
#
echo "loading the unzipped scans into database, add wegdelen / pv to scans"

dc run --rm csvimporter app

echo "Logging database output. just in case of errors"
dc logs database

# crate table list for logstash / scan count stats on wegdelen / vakken
dc run --rm importer ./docker-scanstats.sh

echo "DONE! importing scans into DATABASE"

if [ $RUNELASTIC != "yes" ]
then
	echo "create scan db dump"
	# run the DB backup shizzle
	dc exec -T database ./backup-db-scans.sh
fi

echo "DONE! with scan data import. You are awesome! <3"
echo "Leaving docker and data around for elastic import"
echo "if $RUNELASTIC == yes"

if [ $RUNELASTIC == "yes" ]
then
	source ${DIR}/import-es.sh
fi
