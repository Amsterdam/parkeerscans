package main

import (
	"database/sql"
	"fmt"
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

type VakIDHour struct {
	uniqevakken map[string]bool
}

type wegdeelAggregator struct {
	uniqehours map[string]*VakIDHour
}

func (vkh VakIDHour) addpvID(pvID string) {

	if vkh.uniqevakken == nil {
		vkh.uniqevakken = make(map[string]bool)
	}

	vkh.uniqevakken[pvID] = true
}

func (wa wegdeelAggregator) addHourKey(hourkey string, pvID string) {
	if _, ok := wa.uniqehours[hourkey]; !ok {
		wa.uniqehours[hourkey] = &VakIDHour{
			uniqevakken: make(map[string]bool),
		}
	}

	wa.uniqehours[hourkey].addpvID(pvID)
}

type endResult struct {
	wegdelen map[string]*wegdeelAggregator
}

func (e endResult) addWegdeel(wd string, hourkey string, pvID string) {

	fmt.Println("test")
	if e.wegdelen == nil {
		e.wegdelen = make(map[string]*wegdeelAggregator)
	}

	if _, ok := e.wegdelen[wd]; !ok {
		e.wegdelen[wd] = &wegdeelAggregator{
			uniqehours: make(map[string]*VakIDHour),
		}
	}

	e.wegdelen[wd].addHourKey(hourkey, pvID)
}

type wegdeelOccupancyResult struct {
	ID            int64
	bgtID         string
	bgtFunctie    string
	geometrie     string
	vakken        int64
	fiscaleVakken int64
	scanCount     int64
	avgOccupany   int64
	minOccupany   int64
	maxOccupany   int64
	stdOccupany   int64
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

func fillWegDeelVakkenByHour() endResult {

	//var wdID string
	aEndResult := endResult{}
	fmt.Println("test0")
	fmt.Println(aEndResult)

	for _, scan := range AllScans {
		//get wegdeel hour collector.
		if scan == nil {
			continue
		}
		wdID := scan.bgtWegdeel
		hourkey := scan.getMapHourID()
		pvID := scan.ParkeervakID
		aEndResult.addWegdeel(wdID, hourkey, pvID)
	}
	return aEndResult
}
