#!/usr/bin/env bash

set -u
set -e
set -x

echo 0.0.0.0:5432:predictiveparking:predictiveparking:insecure > ~/.pgpass

chmod 600 ~/.pgpass

pg_dump   --clean \
	  -Fc \
	  -t wegdelen* \
	  -t metingen* \
	  -t occupancy* \
	  -t scans* \
	  -t django_migrations  \
	  -U predictiveparking \
	  -h database -p 5432 \
	  predictiveparking > /tmp/backups/database.dump

