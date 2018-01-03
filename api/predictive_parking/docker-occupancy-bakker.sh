#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

echo "create needed selections"
python manage.py scrape_occupancy --selections

echo "download new selections"

python manage.py scrape_occupancy --wegdelen

#python manage.py scrape_occupancy --wegdelen --part 1 &
#python manage.py scrape_occupancy --wegdelen --part 2 &
#python manage.py scrape_occupancy --wegdelen --part 3 &
#python manage.py scrape_occupancy --wegdelen --part 4
wait

echo "create database tables"
python manage.py scrape_occupancy --store_occupation
