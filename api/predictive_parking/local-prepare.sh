#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

#echo 'Downloading latest parking scan data'
#python get_os_data.py


echo "split files in 500.000 chunks"

#ls /app/unzipped/*stad*.csv | xargs -I csvsource -x tail -n +2 csvsource |  split -l 500000 - /app/unzipped/split_csvsource_

for file in /app/unzipped/*stad*.csv
do
	echo $file
	lala=`basename $file .csv`
	echo $lala
	tail -n +2 $file | split --additional-suffix=.csv -l 500000 - "/app/unzipped/split$lala"

done

echo "Database and Raw CSV files are ready"
