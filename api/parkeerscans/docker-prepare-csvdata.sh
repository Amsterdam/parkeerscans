#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo 'Downloading latest parking scan data'
python get_os_data.py

echo 'start extracting..'

rm /app/data/*qlk.rar* || true
ls /app/data/*.{rar,zip} | xargs -I rarfile unar -D rarfile -o /app/unzipped/ || true
rename -v 's/(\w+)(\d{4})/$1_$2/s' /app/unzipped/*.csv

ls -alh /app/unzipped

if [ "$TESTING" = "yes" ]
then
  echo "testing so shrink csv's to 5000 lines"
  ls /app/unzipped/*.csv | xargs -I csvfile sed -i '5001,$ d' csvfile
fi

ls -alh /app/unzipped

echo "Database and Raw csv files are ready"
