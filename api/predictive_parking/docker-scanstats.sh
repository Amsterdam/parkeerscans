#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print any command

# crate table list for logstash / scancount queries
python manage.py run_import --storescantables

python manage.py run_import --createsamplescans

python manage.py run_import --addsummaryscancounts
