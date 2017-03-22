/*
SQL procedures to chunck up the
merge of scans with "wegdelen / parkeervakken"

*/
package main

import (
	"database/sql"
	"fmt"
	"time"
)

//mergeScansParkeervakWegdelen merge wegdelen / pv with scans
func mergeScansParkeervakWegdelen(
	db *sql.DB,
	sourceTable string,
	targetTable string,
	distance float32) {

	info := fmt.Sprintf("merge vakken %s", sourceTable)
	defer timeTrack(time.Now(), info)

	sql := fmt.Sprintf(`

    WITH matched_scans AS (
    SELECT
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

    FROM %s s ,wegdelen_parkeervak pv
    WHERE ST_DWithin(s.geometrie, pv.geometrie, %f)
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

	//fmt.Printf(sql)

	fmt.Printf("\nMerge %fm  %s\n", distance, sourceTable)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	scanStatus(db, targetTable)
}

//mergeScansWegdelen merge wegdelen / pv with scans
func mergeScansWegdelen(
	db *sql.DB,
	sourceTable string,
	targetTable string,
	distance float32) {

	info := fmt.Sprintf("merge vakken %s", sourceTable)
	defer timeTrack(time.Now(), info)

	sql := fmt.Sprintf(`

    WITH matched_scans AS (
    SELECT
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

    FROM %s s, wegdelen_wegdeel wd
    WHERE ST_DWithin(s.geometrie, wd.geometrie, %f)
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

	fmt.Println("\nMerge Wegdelen\n", sourceTable)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	scanStatus(db, targetTable)
}

func scanStatus(db *sql.DB, targetTable string) {

	info := "counting.."
	defer timeTrack(time.Now(), info)
	countScans := fmt.Sprintf("SELECT count(*) from %s;", targetTable)

	rows, err := db.Query(countScans)
	checkErr(err)
	count := checkCount(rows)

	fmt.Println("\n Scans Verwerkt: ", count)
}

func checkCount(rows *sql.Rows) (count int) {
	for rows.Next() {
		err := rows.Scan(&count)
		checkErr(err)
	}
	return count
}
