#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

source docker-wait.sh

source docker-migrate.sh

# make scan table(s) unlogged
python manage.py run_import --setunlogged

## import wegdelen uit wegdeel project
python manage.py run_import --wegdelen

## import parkeervakken uit parkeervakken project
python manage.py run_import --vakken

## import buurten uit bag
python manage.py run_import --buurten
## plak buurt info aan parkeervakken


## cluster geoindexen
python manage.py run_import --cluster

## plak wegdeel info aan parkeervakken
python manage.py run_import --mergewegdelen

python manage.py run_import --mergebuurten

# set parkeervak counts op buurten en wegdelen
# fiscaal en niet fiscaal
python manage.py run_import --parkeervakcounts


## plak vakken aan scans
python manage.py run_import --mergevakken

# scans zonder parkeervak hebben wel een wegdeel
python manage.py run_import --addwegdeeltowrongscans

# create scanmoment index for logstash
python manage.py run_import --scanmomnetindex


