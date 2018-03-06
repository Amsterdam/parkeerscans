#!/usr/bin/env bash

set -u
set -e
set -x

echo 0.0.0.0:5432:predictiveparking:predictiveparking:insecure > ~/.pgpass

chmod 600 ~/.pgpass

pg_dump --clean \
	-Fc \
	-t wegdelen* \
	-t metingen* \
	-t scans* \
	-t django_migrations  \
	-U predictiveparking \
	-h 0.0.0.0 -p 5432 \
	-f /backups/database.dump \
	predictiveparking
