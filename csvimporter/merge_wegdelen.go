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
	start string, end string,
	distance float32) {

	sql := fmt.Sprintf(`

	WITH matched_scans AS (
    DELETE FROM metingen_scanraw s
    USING wegdelen_parkeervak pv
    WHERE ST_DWithin(s.geometrie, pv.geometrie, %f)
	AND scan_moment >= '%s'::date
	AND scan_moment <= '%s'::date

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


        parkeervak_id,
        parkeervak_soort,
        bgt_wegdeel,
        bgt_wegdeel_functie

        )
    SELECT * FROM matched_scans;
	`, distance, start, end)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}
}

//MergeScansWegdelen merge wegdelen / pv with scans
func MergeScansWegdelen(
	db *sql.DB,
	start string, end string,
	distance float32) {

	sql := fmt.Sprintf(`

    WITH matched_scans AS (
    DELETE FROM metingen_scanraw s
    USING wegdelen_wegdeel wd
    WHERE ST_DWithin(s.geometrie, wd.geometrie, %f)
	AND scan_moment >= '%s'::date
	AND scan_moment <= '%s'::date
    RETURNING
        s.scan_id,
        s.scan_moment,

        s.device_id,
        s.scan_source,

        s.longitude,
        s.latitude,
		s.geometrie

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
    INSERT INTO metingen_scan(
        scan_id,
        scan_moment,

        device_id,
        scan_source,

        longitude,
        latitude,
		geometrie

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
    SELECT * FROM matched_scans;`, distance, start, end)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}
}
