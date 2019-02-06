
export PGPASSWORD=insecure
export DB_USER=predictiveparking
export DB_SERVER=database
export DB_NAME=$1


if [ -z "$1" ]
then
      echo "No database name supplied using 'test_predictiveparking'"
      DB_NAME="test_predictiveparking"
fi


loaddata() {
  psql -h database -U predictiveparking -d $1 -c "COPY $2 FROM STDIN"
}

docker_loaddata() {
  docker exec -i --user postgres predictive_parking_database_1 psql "postgresql://$DB_USER:$PGPASSWORD@$DB_SERVERl/$DB_NAME" -c  "COPY $2 FROM STDIN"
}


if [[ $USE_DOCKER = "true" ]]
   then
    docker_loaddata $DB_NAME wegdelen_wegdeel < testdata/wegdeel.csv
    docker_loaddata $DB_NAME wegdelen_parkeervak < testdata/vakken.csv
    # loaddata $DB metingen_scan < testdata/scans.csv
    # version 2 scans. 10-2017
    docker_loaddata $DB_NAME metingen_scan < testdata/scans.csv
    docker_loaddata $DB_NAME wegdelen_buurt < testdata/buurt.csv
else
    echo $DB_NAME
    loaddata $DB_NAME wegdelen_wegdeel < testdata/wegdeel.csv
    loaddata $DB_NAME wegdelen_parkeervak < testdata/vakken.csv
    # loaddata $DB metingen_scan < testdata/scans.csv
    # version 2 scans. 10-2017
    loaddata $DB_NAME metingen_scan < testdata/scans.csv
    loaddata $DB_NAME wegdelen_buurt < testdata/buurt.csv
fi

