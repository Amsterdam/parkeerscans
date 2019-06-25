#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo 'Downloading latest parking scan data'
python get_os_data.py

echo 'start extracting..'

ls /app/data/*.rar | xargs -I rarfile unar -s rarfile -o /app/unzipped/ || true
rename -v 's/(.*?)(\d{4})(.*?)/export_scandata_stad_$2/g' /app/data/*.rar

ls -alh /app/unzipped

if [ "$TESTING" = "yes" ]
then
  echo "testing so shrink csv's to 1000 lines"
  ls /app/unzipped/*.csv | xargs -I csvfile sed -i '1001,$ d' csvfile
fi

ls -alh /app/unzipped

echo "Database and Raw csv files are ready"
