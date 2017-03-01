#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

source docker-wait.sh

source docker-migrate.sh

# echo 'Downloading latest parking scan data'
python get_os_data.py

[ "$(ls -A /app/unzipped/)" ] && echo "Not Empty" || echo "Empty"

if ["$(ls -A /app/unzipped/)" ]
then
	echo "lets unzip csvs!"
	# these commands do not overwirte existing files!!
	# unzip -n '/app/data/*.zip' -d /app/unzipped/
	ls /app/data/*.rar | xargs -I rarfile unrar -x rarfile /app/unzipped/ || true
else
	echo "csv already present"
fi

ls -alh /app/unzipped

if [ "$TESTING" = "yes" ]
then
  echo "testing so shrink csv's to 1000 lines"
  ls /app/unzipped/*.csv | xargs -I csvfile sed -i '1001,$ d' csvfile
fi

ls -alh /app/unzipped

echo "Database and Raw csv files are ready"
