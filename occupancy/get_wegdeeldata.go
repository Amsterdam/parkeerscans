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

type vakIDHour struct {
	uniqevakken map[string]bool
}

type wegdeelAggregator struct {
	uniqehours    map[string]*vakIDHour
	scanCount     int64
	fiscaleVakken int64
	vakken        int64
}

func (wda *wegdeelAggregator) stats() (int64, int64, int64, int64) {
	min := int64(100)
	max := int64(0)
	sum := int64(0)

	std := int64(0)
	avg := int64(0)

	occupancies := []int64{}

	bucketCount := int64(len(wda.uniqehours))

	for _, bucket := range wda.uniqehours {
		occupancy := int64(
			float64(wda.fiscaleVakken) / float64(len(bucket.uniqevakken)) * 100)
		occupancies = append(occupancies, occupancy)

		if occupancy < min {
			min = occupancy
		}

		if occupancy > max {
			max = occupancy
		}
		sum = sum + occupancy

	}

	avg = sum / bucketCount

	return min, max, std, avg

}

func (vkh *vakIDHour) addpvID(pvID string) {

	if vkh.uniqevakken == nil {
		vkh.uniqevakken = make(map[string]bool)
	}

	vkh.uniqevakken[pvID] = true
}

func (wa *wegdeelAggregator) addHourKey(hourkey string, pvID string) {
	if _, ok := wa.uniqehours[hourkey]; !ok {
		wa.uniqehours[hourkey] = &vakIDHour{
			uniqevakken: make(map[string]bool),
		}
	}
	wa.scanCount++
	wa.uniqehours[hourkey].addpvID(pvID)
}

type buckets struct {
	wegdelen map[string]*wegdeelAggregator
}

func (e *buckets) addWegdeel(wd string, hourkey string, pvID string) {

	if e.wegdelen == nil {
		e.wegdelen = make(map[string]*wegdeelAggregator)
	}

	if _, ok := e.wegdelen[wd]; !ok {
		e.wegdelen[wd] = &wegdeelAggregator{
			uniqehours:    make(map[string]*vakIDHour),
			fiscaleVakken: wegdelen[wd].fiscaleVakken,
			vakken:        wegdelen[wd].vakken,
		}
	}

	e.wegdelen[wd].addHourKey(hourkey, pvID)
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

func fillWegDeelVakkenByBucket(filteredScans Scans) wegdeelResponse {

	//var wdID string
	fmt.Println("yes")
	bucketResult := buckets{}

	for _, scan := range filteredScans {
		wdID := scan.bgtWegdeel
		hourkey := scan.getMapHourID()
		pvID := scan.ParkeervakID

		if _, ok := wegdelen[wdID]; !ok {
			continue
		}
		bucketResult.addWegdeel(wdID, hourkey, pvID)
	}

	fmt.Println(len(bucketResult.wegdelen))
	aEndResult := wegdeelResponse{}

	for wdID, wdAgg := range bucketResult.wegdelen {

		wdSource := wegdelen[wdID]

		if wdSource == nil {
			continue
		}

		min, max, std, avg := wdAgg.stats()

		wdOccupancy := &wegdeelOccupancyResult{
			ID:    wdSource.ID,
			BgtID: wdSource.bgtID,
			//bgtFunctie:    wdSource.bgtFunctie,
			Geometrie:     wdSource.geometrie,
			Vakken:        wdSource.vakken,
			FiscaleVakken: wdSource.fiscaleVakken,
			ScanCount:     wdAgg.scanCount,
			AvgOccupany:   avg,
			MinOccupany:   min,
			MaxOccupany:   max,
			StdOccupany:   std,
		}
		aEndResult = append(aEndResult, wdOccupancy)
	}

	fmt.Println("yes2")
	return aEndResult
}
