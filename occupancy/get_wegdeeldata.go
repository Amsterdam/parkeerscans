package main

import (
	"database/sql"
	"log"
)

type wegdeel struct {
	ID            int64
	bgtID         string
	bgtFunctie    string
	geometrie     string
	vakken        int64
	fiscaleVakken int64
	scanCount     int64
}

type wegdeelResponse []*wegdeelOccupancyResult

type wegdeelOccupancyResult struct {
	ID            int64  `json:"id"`
	BgtID         string `json:"bgtID"`
	BgtFunctie    string `json:"bgtFunctie"`
	Geometrie     string `json:"geometrie"`
	Vakken        int64  `json:"vakken"`
	FiscaleVakken int64  `json:"fiscaleVakken"`
	ScanCount     int64  `json:"scanCount"`
	AvgOccupany   int64  `json:"avg"`
	MinOccupany   int64  `json:"min"`
	MaxOccupany   int64  `json:"max"`
	StdOccupany   int64  `json:"std"`
	BuckerCount   int64  `json:"buckets"`
}

/*
id               int6
bgt_id
bgt_functie
geometrie
vakken
fiscale_vakken
scan_count
*/

func fillWegdelenFromDB() {
	db, err := dbConnect(ConnectStr())

	if err != nil {
		log.Fatal(err)
	}
	query := "select * from wegdelen_wegdeel where fiscale_vakken > 4"

	rows, err := db.Query(query)

	if err != nil {
		log.Fatal(err)
	}

	var ID int64
	var bgtID sql.NullString
	var bgtFunctie sql.NullString
	var geometrie sql.NullString
	var vakken sql.NullInt64
	var fiscaleVakken sql.NullInt64
	var scanCount sql.NullInt64
	wdCounter := 0

	for rows.Next() {
		if err := rows.Scan(
			&ID,
			&bgtID,
			&bgtFunctie,
			&geometrie,
			&vakken,
			&fiscaleVakken,
			&scanCount,
		); err != nil {
			log.Fatal(err)
		}

		wd := &wegdeel{
			ID:            ID,
			bgtID:         convertSqlNullString(bgtID),
			bgtFunctie:    convertSqlNullString(bgtFunctie),
			geometrie:     convertSqlNullString(geometrie),
			vakken:        convertSqlNullInt(vakken),
			fiscaleVakken: convertSqlNullInt(fiscaleVakken),
		}
		wdCounter++

		wegdelen[wd.bgtID] = wd

	}

	log.Printf("STATUS: wegdelen met 4+ fiscale vakken. %-10d", wdCounter)
	rerr := rows.Close()

	if rerr != nil {
		log.Fatal(err)
	}

	// Rows.Err will report the last error encountered by Rows.Scan.
	if err := rows.Err(); err != nil {
		log.Fatal(err)
	}
}
