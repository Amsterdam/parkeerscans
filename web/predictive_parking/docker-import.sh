#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

source docker-wait.sh

source docker-migrate.sh


## import wegdelen
python manage.py run_import --wegdelen
## import parkeervakken
python manage.py run_import --vakken
## plak wegdeel info aan parkeervakken
python manage.py run_import --mergewegdelen
## plak vakken aan scans
python manage.py run_import --mergevakken
#
