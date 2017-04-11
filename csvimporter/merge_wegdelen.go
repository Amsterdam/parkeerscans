/*
SQL procedures to chunck up the
merge of scans with "wegdelen / parkeervakken"

*/
package main

import (
	"database/sql"
	"fmt"
	"log"
	"time"
)

//mergeScansParkeervakWegdelen merge wegdelen / pv with scans
func mergeScansParkeervakWegdelen(
	db *sql.DB,
	sourceTable string,
	targetTable string,
	distance float32) int {

	info := fmt.Sprintf("Merge %fm  %s", distance, sourceTable)

	defer timeTrack(time.Now(), info)

	sql := fmt.Sprintf(`

    WITH matched_scans AS (
    DELETE FROM %s s
    USING wegdelen_parkeervak pv
    WHERE ST_DWithin(s.geometrie, pv.geometrie, %f)
    RETURNING
		s.scan_id,
		s.scan_moment,
		s.device_id,
		s.scan_source,

		s.longitude,
		s.latitude,
		s.geometrie,

		s.stadsdeel,
			s.buurtcode,
		s.buurtcombinatie,

		s.sperscode,
		s.qualcode,
		s.ff_df,
		s.nha_nr,
		s.nha_hoogte,
		s.uitval_nachtrun,

		pv.id,
		pv.soort,
		pv.bgt_wegdeel,
		pv.bgt_wegdeel_functie
    )
    INSERT INTO %s(
        scan_id,
        scan_moment,

        device_id,
        scan_source,

        longitude,
        latitude,
		geometrie,

		stadsdeel,
        buurtcode,
		buurtcombinatie,

        sperscode,
        qualcode,
        ff_df,
        nha_nr,
        nha_hoogte,
        uitval_nachtrun,

	    /* add parkeervak AND wegdeel infromation */

        parkeervak_id,
        parkeervak_soort,
        bgt_wegdeel,
        bgt_wegdeel_functie

	)
    SELECT * FROM matched_scans;
	`, sourceTable, distance, targetTable)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	return scanStatus(db, targetTable)
}

//mergeScansWegdelen merge wegdelen / pv with scans
func mergeScansWegdelen(
	db *sql.DB,
	sourceTable string,
	targetTable string,
	distance float32) int {

	info := fmt.Sprintf("Merge wegdelen %s", sourceTable)
	defer timeTrack(time.Now(), info)

	sql := fmt.Sprintf(`

    WITH matched_scans AS (
    DELETE FROM %s s
    USING wegdelen_wegdeel wd
    WHERE ST_DWithin(s.geometrie, wd.geometrie, %f)
    RETURNING
		s.scan_id,
		s.scan_moment,

		s.device_id,
		s.scan_source,

		s.longitude,
		s.latitude,
		s.geometrie,

		s.stadsdeel,
		s.buurtcode,
		s.buurtcombinatie,

		s.sperscode,
		s.qualcode,
		s.ff_df,
		s.nha_nr,
		s.nha_hoogte,
		s.uitval_nachtrun,

		wd.id,
		wd.bgt_functie
    )
    INSERT INTO %s(
		scan_id,
		scan_moment,

		device_id,
		scan_source,

		longitude,
		latitude,
		geometrie,

		stadsdeel,
		buurtcode,
		buurtcombinatie,

		sperscode,
		qualcode,
		ff_df,
		nha_nr,
		nha_hoogte,
		uitval_nachtrun,

		bgt_wegdeel,
		bgt_wegdeel_functie
    )
    SELECT * FROM matched_scans;`, sourceTable, distance, targetTable)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	return scanStatus(db, targetTable)
}

func scanStatus(db *sql.DB, targetTable string) int {

	countScans := fmt.Sprintf("SELECT count(*) from %s;", targetTable)

	rows, err := db.Query(countScans)
	checkErr(err)
	count := checkCount(rows)

	log.Printf("Scans in %s:  %d", targetTable, count)

	return count
}

func totalProcessedScans(db *sql.DB) int {
	countScans := fmt.Sprintf("SELECT count(*) from metingen_scan;")

	rows, err := db.Query(countScans)
	checkErr(err)
	count := checkCount(rows)

	log.Printf("Scans in metingen_scan:  %d", count)

	return count
}

func checkCount(rows *sql.Rows) (count int) {
	for rows.Next() {
		err := rows.Scan(&count)
		checkErr(err)
	}
	return count
}
