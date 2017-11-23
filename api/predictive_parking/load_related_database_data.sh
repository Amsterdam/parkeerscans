#!/usr/bin/env bash

# helper script to fill database with related data for (development)

# set -u
# set -e
set -x
echo "provde username if using ssh / dev env"

username=$1

dc() {
	docker-compose $*;
}

gettable(){
	dc exec database update-table.sh $*  $username
}

gettable parkeervakken parkeervakken bv predictiveparking
# foutparkeerders / scans niet in vakken
gettable  basiskaart BGT_OWGL_verkeerseiland bgt predictiveparking
gettable  basiskaart BGT_OWGL_berm bgt predictiveparking
gettable  basiskaart BGT_OTRN_open_verharding bgt predictiveparking
gettable  basiskaart BGT_OTRN_transitie bgt predictiveparking
gettable  basiskaart BGT_WGL_fietspad bgt predictiveparking
gettable  basiskaart BGT_WGL_voetgangersgebied bgt predictiveparking
gettable  basiskaart BGT_WGL_voetpad bgt predictiveparking

# scans op wegen en vakken
gettable basiskaart BGT_WGL_parkeervlak bgt predictiveparking
gettable basiskaart BGT_WGL_rijbaan_lokale_weg bgt predictiveparking
gettable basiskaart BGT_WGL_rijbaan_regionale_weg bgt predictiveparking

echo "Load buurt / buurtcombinatie"
gettable bag bag_buurt public predictiveparking
