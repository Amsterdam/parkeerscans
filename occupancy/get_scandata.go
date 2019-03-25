package main

import (
	"database/sql"
	"log"
	"time"

	_ "github.com/lib/pq"
)

/*
 id                   | integer                  |           | not null | nextval('metingen_scan_id_seq'::regclass)
 scan_id              | integer                  |           | not null |
 scan_moment          | timestamp with time zone |           | not null |
 device_id            | integer                  |           |          |
 scan_source          | character varying(15)    |           | not null |
 afstand              | character varying(1)     |           |          |
 latitude             | numeric(13,8)            |           | not null |
 longitude            | numeric(13,8)            |           | not null |
 stadsdeel            | character varying(1)     |           |          |
 buurtcombinatie      | character varying(3)     |           |          |
 buurtcode            | character varying(4)     |           |          |
 sperscode            | character varying(15)    |           |          |
 qualcode             | character varying(35)    |           |          |
 ff_df                | character varying(15)    |           |          |
 nha_nr               | character varying(15)    |           |          |
 nha_hoogte           | numeric(6,3)             |           |          |
 uitval_nachtrun      | character varying(8)     |           |          |
 geometrie            | geometry(Point,4326)     |           |          |
 parkeervak_id        | character varying(15)    |           |          |
 parkeervak_soort     | character varying(15)    |           |          |
 bgt_wegdeel          | character varying(38)    |           |          |
 bgt_wegdeel_functie  | character varying(25)    |           |          |
 gps_plate            | geometry(Point,4326)     |           |          |
 gps_scandevice       | geometry(Point,4326)     |           |          |
 gps_vehicle          | character varying(15)    |           |          |
 location_parking_bay | character varying(15)    |           |          |
 parkingbay_angle     | double precision         |           |          |
 parkingbay_distance  | double precision         |           |          |
 reliability_ANPR     | double precision         |           |          |
 reliability_gps      | geometry(Point,4326)     |           |          |
 parkeerrecht_id      | bigint                   |           |          |

type Scan struct {
	id                   string	     `json:"id"`
	scan_id              sql.NullString `json:"scan_id"`
	scan_moment          sql.NullString `json:"scan_momemt"`
	device_id            sql.NullString `json:"device_id"`
	scan_source          sql.NullString `json:"scan_source"`
	afstand              sql.NullString `json:"afstand"`
	latitude             sql.NullString `json:"latitude"`
	longitude            sql.NullString `json:"longitude"`
	stadsdeel            sql.NullString `json:"stadsdeel"`
	buurtcombinatie      sql.NullString `json:"buurtcombinatie"`
	buurtcode            sql.NullString `json:t"t""buurtcode"`
	sperscode            sql.NullString `json:"sperscode"`
	qualcode             sql.NullString `json:"qualcode"`
	ff_df                sql.NullString `json:"ff_df"`
	nha_nr               sql.NullString `json:"nha_nr"`
	nha_hoogte           sql.NullString `json:"nha_hoogte"`
	uitval_nachtrun      sql.NullString `json:"uitval_nachtrun"`
	geometrie            sql.NullString `json:"geometrie"`
	parkeervak_id        sql.NullString `json:"parkeervak_id"`
	parkeervak_soort     sql.NullString `json:"parkeervak_soort"`
	bgt_wegdeel          sql.NullString `json:"bgt_wegdeel"`
	bgt_wegdeel_functie  sql.NullString `jsonbgt_wegdeel_functie"`
	gps_plate            sql.NullString `json:"gps_plate"`
	gps_scandevice       sql.NullString `json:"gps_scandevice"`
	gps_vehicle          sql.NullString `json:"gps_vehicle"`
	location_parking_bay sql.NullString `json:"location_parking_bay"`
	parkingbay_angle     sql.NullString `json:"parkingbay_angle"`
	parkingbay_distance  sql.NullString `json:"parkingbay_distance"`
	reliability_ANPR     sql.NullString `json:"reliability_ANPR"`
	reliability_gps      sql.NullString `json:"reliability_gps"`
	parkeerrecht_id      sql.NullString `json:"parkeerrecht_id"`
}
*/

type geoPoint struct {
	lon float64 `json:"lon"`
	lat float64 `json:"lat"`
}

//Scan instance of a car.
type Scan struct {
	ID                string    `json:"id"`
	ScanID            int64     `json:"scan_id"`
	ScanMoment        time.Time `json:"@timestamp"`
	ScanSource        string    `json:"scan_source"`
	Sperscode         string    `json:"sperscode"`
	Qualcode          string    `json:"qualcode"`
	Ff_df             string    `json:"ff_df"`
	NaheffingHoogte   int64     `json:"naheffing_hoogte"`
	bgtWegdeel        string    `json:"bgt_wegdeel"`
	BGTwegdeelFunctie string    `json:"bgt_wegdeel_functie"`
	Buurtcode         string    `json:"buurtcode"`
	Buurtcombinatie   string    `json:"buurtcombinatie"`
	Stadsdeel         string    `json:"stadsdeel"`
	ParkeervakID      string    `json:"parkeervak_id"`
	ParkeervakSoort   string    `json:"parkeervak_soort"`

	geoPoint
}

type Scans []*Scan
type ScansGroupedBy map[string]Scans

func (i Scan) getMapHourID() string {
	return i.ScanMoment.Format("2006-01-02T15")
}

func (i Scan) getStrWeek() string {
	return i.ScanMoment.Weekday().String()
}

func (i Scan) isWeekend() bool {
	return int(i.ScanMoment.Weekday()) >= 5
}

func setDateConstrain() string {
	q := `
          SELECT
             id,
	     	 scan_id,
			 EXTRACT(EPOCH FROM scan_moment)::int as scan_moment,
             scan_source,
             sperscode,
             qualcode,
             ff_df,
             ROUND(nha_hoogte) as naheffing_hoogte,
             bgt_wegdeel,
             bgt_wegdeel_functie,
             buurtcode,
             buurtcombinatie,
             stadsdeel,
             parkeervak_id,
             parkeervak_soort,
             round(ST_Y(geometrie)::numeric,8) as lat,
             round(ST_X(geometrie)::numeric,8) as lon
          FROM metingen_scan
	`
	monthsAgo := SETTINGS.GetInt("monthsago")
	now := time.Now()
	timeStamp := now.AddDate(0, -monthsAgo, 0)

	return queryDateBuilder(q, "scan_moment", timeStamp.Format("2006-01-02"), "")
}

func fillScansFromDB(items chan *Scan) {
	db, err := dbConnect(ConnectStr())
	if err != nil {
		log.Fatal(err)
	}
	query := setDateConstrain()
	rows, err := db.Query(query)

	if err != nil {
		log.Fatal(err)
	}
	var ID string
	var scan_id sql.NullInt64
	var scan_moment sql.NullInt64
	var scan_source sql.NullString
	var sperscode sql.NullString
	var qualcode sql.NullString
	var ff_df sql.NullString
	var naheffing_hoogte sql.NullInt64
	var bgtWegdeel sql.NullString
	var bgt_wegdeel_functie sql.NullString
	var buurtcode sql.NullString
	var buurtcombinatie sql.NullString
	var stadsdeel sql.NullString
	var parkeervakID sql.NullString
	var parkeervak_soort sql.NullString
	var lat sql.NullFloat64
	var lon sql.NullFloat64

	for rows.Next() {
		if err := rows.Scan(
			&ID,
			&scan_id,
			&scan_moment,
			&scan_source,
			&sperscode,
			&qualcode,
			&ff_df,
			&naheffing_hoogte,
			&bgtWegdeel,
			&bgt_wegdeel_functie,
			&buurtcode,
			&buurtcombinatie,
			&stadsdeel,
			&parkeervakID,
			&parkeervak_soort,
			&lat,
			&lon,
		); err != nil {
			// Check for a scan error.
			// Query rows will be closed with defer.
			log.Fatal(err)
		}

		item := &Scan{
			ID:         ID,
			ScanID:     convertSqlNullInt(scan_id),
			ScanMoment: time.Unix(convertSqlNullInt(scan_moment), 0),
			ScanSource: convertSqlNullString(scan_source),
			Sperscode:  convertSqlNullString(sperscode),
			Qualcode:   convertSqlNullString(qualcode),

			Ff_df: convertSqlNullString(ff_df),

			NaheffingHoogte:   convertSqlNullInt(naheffing_hoogte),
			bgtWegdeel:        convertSqlNullString(bgtWegdeel),
			BGTwegdeelFunctie: convertSqlNullString(bgt_wegdeel_functie),
			Buurtcode:         convertSqlNullString(buurtcode),
			Buurtcombinatie:   convertSqlNullString(buurtcombinatie),
			Stadsdeel:         convertSqlNullString(stadsdeel),
			ParkeervakID:      convertSqlNullString(parkeervakID),

			geoPoint: geoPoint{
				lat: convertSqlNullFloat(lat),
				lon: convertSqlNullFloat(lon),
			},
		}

		if item == nil {
			continue
		}

		items <- item
	}
	// If the database is being written to ensure to check for Close
	// errors that may be returned from the driver. The query may
	// encounter an auto-commit error and be forced to rollback changes.
	rerr := rows.Close()

	if rerr != nil {
		log.Fatal(err)
	}
	// Rows.Err will report the last error encountered by Rows.Scan.
	if err := rows.Err(); err != nil {
		log.Fatal(err)
	}
}
