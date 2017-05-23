
export PGPASSWORD=insecure

loaddata() {
  psql -h database -U predictiveparking -d test_predictiveparking -c "COPY $1 FROM STDIN"
}

loaddata wegdelen_wegdeel < testdata/wegdeel.csv
loaddata wegdelen_parkeervak < testdata/vakken.csv
loaddata metingen_scan < testdata/scans.csv
