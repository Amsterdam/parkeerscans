#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

source docker-wait.sh

source docker-migrate.sh

# echo 'Downloading latest parking scan data'
python get_os_data.py


# these commands do not overwirte existing files!!
unzip -n '/app/data/*.zip' -d /app/unzipped/
ls /app/data/*.rar | xargs -I rarfile unrar -x rarfile /app/unzipped/  || true

echo "Database and Raw csv files are ready"
