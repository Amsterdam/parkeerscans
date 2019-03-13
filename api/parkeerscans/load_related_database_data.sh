#!/usr/bin/env bash

# helper script to fill database with related data for (development)

# set -u
set -e
set -x

echo "Provde username if using ssh / dev env"

username=$1

dc() {
	docker-compose $*;
}

gettable(){
	dc exec -T database update-table.sh $*  $username || true
}

gettable parkeervakken parkeervakken bv parkeerscans
# foutparkeerders / scans niet in vakken
gettable  basiskaart BGT_OWGL_verkeerseiland bgt parkeerscans
gettable  basiskaart BGT_OWGL_berm bgt parkeerscans
gettable  basiskaart BGT_OTRN_open_verharding bgt parkeerscans
gettable  basiskaart BGT_OTRN_transitie bgt parkeerscans
gettable  basiskaart BGT_WGL_fietspad bgt parkeerscans
gettable  basiskaart BGT_WGL_voetgangersgebied bgt parkeerscans
gettable  basiskaart BGT_WGL_voetpad bgt parkeerscans

# scans op wegen en vakken
gettable basiskaart BGT_WGL_parkeervlak bgt parkeerscans
gettable basiskaart BGT_WGL_rijbaan_lokale_weg bgt parkeerscans
gettable basiskaart BGT_WGL_rijbaan_regionale_weg bgt parkeerscans

echo "Load buurt / buurtcombinatie"
gettable bag bag_buurt public parkeerscans
