
export PGPASSWORD=insecure

DB=$1

if [ -z "$1" ]
then
      echo "No database name supplied using 'test_predictiveparking'"
      DB="test_predictiveparking"
fi

loaddata() {
  psql -h database -U predictiveparking -d $1 -c "COPY $2 FROM STDIN"
}

loaddata $DB wegdelen_wegdeel < testdata/wegdeel.csv
loaddata $DB wegdelen_parkeervak < testdata/vakken.csv
# loaddata $DB metingen_scan < testdata/scans.csv
# version 2 scans. 10-2017
loaddata $DB metingen_scan < testdata/scans.csv
loaddata $DB wegdelen_buurt < testdata/buurt.csv
