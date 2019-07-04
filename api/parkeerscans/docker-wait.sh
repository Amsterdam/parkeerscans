#!/usr/bin/env bash

set -u
set -e
set -x



# wait for postgres
while ! nc -z $DATABASE_HOST $DATABASE_PORT
do
	echo "Waiting for postgres..."
	sleep 2.5
done
