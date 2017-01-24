#!/usr/bin/env bash

# helper script to fill database with related data for (development)

set -u
set -e
set -x

echo "Load latest parkeervakken.."
docker-compose exec database update-table.sh parkeervakken parkeervakken bv predictiveparking
echo "Load latest wegdelen.."
docker-compose exec database update-table.sh basiskaart bgt_wegdeel bgt predictiveparking
