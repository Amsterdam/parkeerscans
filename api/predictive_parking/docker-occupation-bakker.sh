#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error


python manage.py migrate

echo "create needed selections"
python manage.py scrape_occupation --selections

echo "download new selections"
python manage.py scrape_occupation --wegdelen --part 1 &
python manage.py scrape_occupation --wegdelen --part 2 &
python manage.py scrape_occupation --wegdelen --part 3 &
python manage.py scrape_occupation --wegdelen --part 4
wait

echo "create database views"
python manage.py scrape_occupation --create_views


