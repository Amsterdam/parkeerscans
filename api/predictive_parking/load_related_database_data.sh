#!/usr/bin/env bash

# helper script to fill database with related data for (development)

set -u
set -e
set -x

dc() {
	docker-compose $*;
}

dc exec database update-table.sh parkeervakken parkeervakken bv predictiveparking
# foutparkeerders / scans niet in vakken
dc exec database update-table.sh basiskaart BGT_OWGL_verkeerseiland bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_OWGL_berm bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_OTRN_open_verharding bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_OTRN_transitie bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_WGL_fietspad bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_WGL_voetgangersgebied bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_WGL_voetpad bgt predictiveparking

# scans op wegen en vakken
dc exec database update-table.sh basiskaart BGT_WGL_parkeervlak bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_WGL_rijbaan_lokale_weg bgt predictiveparking
dc exec database update-table.sh basiskaart BGT_WGL_rijbaan_regionale_weg bgt predictiveparking

echo "Load buurt / buurtcombinatie"
dc exec database update-table.sh bag bag_buurt public predictiveparking
#

