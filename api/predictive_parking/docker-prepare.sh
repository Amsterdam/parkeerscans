#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

echo 'Downloading latest parking scan data'
python get_os_data.py

echo 'start extracting..'
#[ "$(ls -A /app/unzipped/)" ] && echo "Not Empty" || echo "Empty"

#if [ "$(ls -A /app/unzipped/)" ]
#then
#	echo "csv already present"
#else
#	echo "lets unzip csvs!"
#	# these commands do not overwirte existing files!!
#	# unzip -n '/app/data/*.zip' -d /app/unzipped/
#	ls /app/data/*.rar | xargs -I rarfile unrar -x rarfile /app/unzipped/ || true
#fi

ls /app/data/*.rar | xargs -I rarfile unrar -x rarfile /app/unzipped/ || true

ls -alh /app/unzipped

if [ "$TESTING" = "yes" ]
then
  echo "testing so shrink csv's to 1000 lines"
  ls /app/unzipped/*.csv | xargs -I csvfile sed -i '1001,$ d' csvfile
fi

echo "split files in 500.000 chunks"

#ls /app/unzipped/*stad*.csv | xargs -I csvsource -x tail -n +2 csvsource |  split -l 500000 - /app/unzipped/split_csvsource_
for file in /app/unzipped/*stad*.csv
do
	echo $file
	lala=`basename $file .csv`
	echo $lala
	tail -n +2 $file | split --additional-suffix=.csv -l 500000 - "/app/unzipped/split$lala"
done

ls -alh /app/unzipped

echo "Database and Raw csv files are ready"
