package main

import (
	"database/sql"
	"log"
	"strconv"
)

type wegdeel struct {
	ID            int64
	bgtID         string
	bgtFunctie    string
	geometrie     string
	buurt         string
	vakken        int64
	fiscaleVakken int64
	scanCount     int64
}

type wegdeelResponse []*wegdeelOccupancyResult

type wegdeelOccupancyResult struct {
	ID            int64  `json:"id"`
	BgtID         string `json:"bgtID"`
	BgtFunctie    string `json:"bgtFunctie"`
	Buurt         string `json:"bgtFunctie"`
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

func (i wegdeelOccupancyResult) Columns() []string {
	return []string{
		"ID",
		"BgtID",
		"BgtFunctie",
		"Geometrie",
		"Buurt",
		"Vakken",
		"FiscaleVakken",
		"ScanCount",
		"AvgOccupany",
		"MinOccupany",
		"MaxOccupany",
		"StdOccupany",
		"BuckerCount",
		"BucketCount",
		"Geometrie",
	}
}

func (i wegdeelOccupancyResult) Row() []string {
	return []string{
		strconv.Itoa(int(i.ID)),
		i.BgtID,
		i.BgtFunctie,
		i.Geometrie,
		i.Buurt,
		strconv.Itoa(int(i.Vakken)),
		strconv.Itoa(int(i.FiscaleVakken)),
		strconv.Itoa(int(i.ScanCount)),
		strconv.Itoa(int(i.AvgOccupany)),
		strconv.Itoa(int(i.MinOccupany)),
		strconv.Itoa(int(i.MaxOccupany)),
		strconv.Itoa(int(i.StdOccupany)),
		strconv.Itoa(int(i.BuckerCount)),
		i.Geometrie,
	}
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

	query := `select

	id, bgt_id, bgt_functie, st_asewkt(geometrie) as geometrie, vakken, fiscale_vakken, buurt

	from wegdelen_wegdeel where vakken > 3`

	rows, err := db.Query(query)

	if err != nil {
		log.Fatal(err)
	}

	var ID int64
	var bgtID sql.NullString
	var bgtFunctie sql.NullString
	var geometrie sql.NullString
	var buurt sql.NullString
	var vakken sql.NullInt64
	var fiscaleVakken sql.NullInt64
	wdCounter := 0

	for rows.Next() {
		if err := rows.Scan(
			&ID,
			&bgtID,
			&bgtFunctie,
			&geometrie,
			&vakken,
			&fiscaleVakken,
			&buurt,
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
			buurt:         convertSqlNullString(buurt),
		}
		wdCounter++

		wegdelen[wd.bgtID] = wd

	}

	log.Printf("STATUS: wegdelen met 3+ vakken. %-10d", wdCounter)
	rerr := rows.Close()

	if rerr != nil {
		log.Fatal(err)
	}

	// Rows.Err will report the last error encountered by Rows.Scan.
	if err := rows.Err(); err != nil {
		log.Fatal(err)
	}
}
