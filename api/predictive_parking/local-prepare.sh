#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

# echo 'Downloading latest parking scan data'
python get_os_data.py


# these commands do not overwirte existing files!!
unzip -n '/tmp/data/*.zip' -d /tmp/unzipped/
ls /tmp/data/*.rar | xargs -I rarfile unrar -x rarfile /tmp/unzipped/

echo "Database and Raw CSV files are ready"
