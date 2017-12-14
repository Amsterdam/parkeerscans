#!/usr/bin/env bash

set -u
set -e
set -x

echo 0.0.0.0:5432:predictiveparking:predictiveparking:insecure > ~/.pgpass

chmod 600 ~/.pgpass

# dump occupation data
pg_dump  -t occupancy* \
	 -t sv*\
	 -U predictiveparking \
	 -h database -p 5432 \
	 predictiveparking > /tmp/backups/occupancy.dump"


