
export PGPASSWORD=insecure

dedb() {
  psql -h database -U predictiveparking -d predictiveparking -c "COPY(SELECT * FROM $1 WHERE geometrie && ST_MakeEnvelope(4.8879,52.3882 , 4.8957,52.3932, 4326) LIMIT 1000) TO STDOUT;"
}

dedb wegdelen_wegdeel > wegdeel.csv

dedb wegdelen_parkeervak > vakken.csv

dedb metingen_scan > scans.csv

dedb wegdelen_buurt > buurt.csv

