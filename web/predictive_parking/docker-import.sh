#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

#source docker-wait.sh

#source docker-migrate.sh

echo 'Downloading latest parking scan data'
# python get_os_data.py


# these commands do not overwirte existing files!!
unzip -n 'data/*.zip' -d unzipped/
unrar e -o- 'data/*.rar' unzipped/ || echo "nothing to unrar"

rm unzipped/*.xlsx

echo 'Remove invalid rows'

# sed -i '/Distanceerror/d' unzipped/*.csv

# load scan data into
python manage.py run_import --scan
