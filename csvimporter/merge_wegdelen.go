/*
SQL procedures to chunck up the
merge of scans with "wegdelen / parkeervakken"

*/
package main

import (
	"database/sql"
	"fmt"
)

//MergeScansParkeervakWegdelen merge wegdelen / pv with scans
func MergeScansParkeervakWegdelen(
	db *sql.DB,
	sourceTable string,
	start string, end string,
	distance float32) {

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
	/*
	AND scan_moment >= '%s'::date
	AND scan_moment <= '%s'::date */

    )
    INSERT INTO metingen_scan(
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
	`, sourceTable, distance, start, end)

	//fmt.Printf(sql)

	fmt.Printf("\nMerge %fm  %s\n", distance, sourceTable)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	scanStatus(db)
}

//MergeScansWegdelen merge wegdelen / pv with scans
func MergeScansWegdelen(
	db *sql.DB,
	sourceTable string,
	start string, end string,
	distance float32) {

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
	/*
	AND scan_moment >= '%s'::date
	AND scan_moment <= '%s'::date */
    )
    INSERT INTO metingen_scan(
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
    SELECT * FROM matched_scans;`, sourceTable, distance, start, end)

	fmt.Println("\nMerge Wegdelen\n", sourceTable)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	scanStatus(db)
}

func scanStatus(db *sql.DB) {

	countScans := "SELECT count(*) from metingen_scan;"

	rows, err := db.Query(countScans)
	CheckErr(err)
	count := checkCount(rows)

	fmt.Println("\n Scans Verwerkt: ", count)
}

//func countTable(db *sql.DB, tableName string) {
//	countScans := fmt.Sprintf("SELECT count(*) from %s;", tableName)
//}

func checkCount(rows *sql.Rows) (count int) {
	for rows.Next() {
		err := rows.Scan(&count)
		CheckErr(err)
	}
	return count
}
