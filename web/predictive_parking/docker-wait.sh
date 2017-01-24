#!/usr/bin/env bash

set -u
set -e


# wait for elastic
while ! nc -z elasticsearch 9300
do
 	echo "Waiting for elastic..."
 	sleep 1.5
done


# wait for postgres
while ! nc -z database 5432
do
	echo "Waiting for postgres..."
	sleep 1.5
done
