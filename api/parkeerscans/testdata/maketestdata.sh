export PGPASSWORD=insecure
export DB_USER=parkeerscans
export DB_SERVER=database
export DB_NAME=parkeerscans

dedb() {
  psql -h database -U parkeerscans -d parkeerscans -c "COPY(SELECT * FROM $1 WHERE geometrie && ST_MakeEnvelope(4.8879,52.3882 , 4.8957,52.3932, 4326) LIMIT 1000) TO STDOUT;"
}
dockerdb() {
  docker exec -it --user postgres predictive_parking_database_1 psql "postgresql://$DB_USER:$PGPASSWORD@$DB_SERVERl/$DB_NAME" -c "COPY(SELECT * FROM $1 WHERE geometrie && ST_MakeEnvelope(4.8879,52.3882 , 4.8957,52.3932, 4326) LIMIT 1000) TO STDOUT;"
}

if [[ $USE_DOCKER = "true" ]]
   then
    dockerdb wegdelen_wegdeel > wegdeel.csv
    dockerdb wegdelen_parkeervak > vakken.csv
    dockerdb metingen_scan > scans.csv
    dockerdb wegdelen_buurt > buurt.csv
else
    dedb wegdelen_wegdeel > wegdeel.csv
    dedb wegdelen_parkeervak > vakken.csv
    dedb metingen_scan > scans.csv
    dedb wegdelen_buurt > buurt.csv
fi
