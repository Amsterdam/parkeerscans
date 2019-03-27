#!/usr/bin/env bash

set -u
set -e
set -x

echo 0.0.0.0:5432:parkeerscans:parkeerscans:insecure > ~/.pgpass

chmod 600 ~/.pgpass

pg_dump --clean \
	-Fc \
	-t wegdelen* \
	-t metingen* \
	-t scans* \
	-t occupancy* \
	-t django_migrations  \
	-U parkeerscans \
	-h 0.0.0.0 -p 5432 \
	-f /backups/database.dump \
	parkeerscans
