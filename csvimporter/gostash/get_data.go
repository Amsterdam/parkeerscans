package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/lib/pq" // here
)

//ConnectStr create string to connect to database
func ConnectStr() string {

	otherParams := "sslmode=disable connect_timeout=5"
	return fmt.Sprintf(
		"user=%s dbname=%s password='%s' host=%s port=%s %s",
		"predictiveparking",
		"predictiveparking",
		"insecure",
		"127.0.0.1",
		"5432",
		otherParams,
	)
}

func dbConnect(connStr string) (*sql.DB, error) {
	//connStr := connectStr()
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return db, err
	}

	err = db.Ping()
	return db, err
}

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

type Item struct {
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

type Item struct {
	id                   string	     `json:"id"`
	scan_id              sql.NullString `json:"scan_id"`
	scan_moment          sql.NullString `json:"scan_momemt"`
	scan_source          sql.NullString `json:"scan_source"`
	sperscode            sql.NullString `json:"sperscode"`
	qualcode             sql.NullString `json:"qualcode"`
	ff_df                sql.NullString `json:"ff_df"`
	naheffing_hoogte     sql.NullString `json:"naheffing_hoogte"`
	bgt_wegdeel          sql.NullString `json:"bgt_wegdeel"`
	bgt_wegdeel_functie  sql.NullString `jsonbgt_wegdeel_functie"`
	buurtcode            sql.NullString `json:"buurtcode"`
	buurtcombinatie      sql.NullString `json:"buurtcombinatie"`
	stadsdeel            sql.NullString `json:"stadsdeel"`
	parkeervak_id        sql.NullString `json:"parkeervak_id"`
	parkeervak_soort     sql.NullString `json:"parkeervak_soort"`
	lat	             sql.NullString `json:"lat"`
	lon	             sql.NullString `json:"lon"`

	hour		     sql.NullString `json:"hour"`
	week                 sql.NullString `json:"week"`
	year		     sql.NullString `json:"year"`

	day_of_year	     sql.NullString `json:"day_of_year"`
	minute		     sql.NullString `json:"minute"`
	second		     sql.NullString `json:"second"`

	month		     sql.NullString `json:"month"`
	day		     sql.NullString `json:"day"`
	shiftrange           sql.NullString `json:"shiftrange"`
}


func fillFromDB(items chan *Item) {
	db, err := dbConnect(ConnectStr())
	if err != nil {
		log.Fatal(err)
	}
	rows, err := db.Query(`
          SELECT
             id,
	     scan_id,
             scan_moment,
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
             round(ST_X(geometrie)::numeric,8) as lon,
             EXTRACT(HOUR FROM scan_moment)::int as hour,
             EXTRACT(WEEK FROM scan_moment)::int as week,
             EXTRACT(YEAR FROM scan_moment)::int as year,
             EXTRACT(DOY FROM scan_moment)::int as day_of_year,
             EXTRACT(MINUTE FROM scan_moment)::int as minute,
             EXTRACT(SECOND FROM scan_moment)::int as second,
             to_char(scan_moment, 'month') as month,
             to_char(scan_moment, 'day') as day,

             CASE
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (9, 10, 11) THEN  '09-11'
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (11, 12, 13) THEN '11-13'
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (13, 14, 15) THEN '13-15'
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (16, 17, 18) THEN '16-18'
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (19, 20, 21) THEN '19-21'
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (21, 22, 23) THEN '21-23'
                WHEN EXTRACT(HOUR FROM scan_moment)::int IN (0, 1, 3, 4, 5, 6) THEN '00-06'
             END as shiftrange

          FROM metingen_scan
	`)

	if err != nil {

		log.Fatal(err)
	}
	var id string
	var scan_id              sql.NullString
	var scan_moment          sql.NullString
	var scan_source          sql.NullString
	var sperscode            sql.NullString
	var qualcode             sql.NullString
	var ff_df                sql.NullString
	var naheffing_hoogte     sql.NullString
	var bgt_wegdeel          sql.NullString
	var bgt_wegdeel_functie  sql.NullString
	var buurtcode            sql.NullString
	var buurtcombinatie      sql.NullString
	var stadsdeel            sql.NullString
	var parkeervak_id        sql.NullString
	var parkeervak_soort     sql.NullString
	var lat	                 sql.NullString
	var lon			 sql.NullString

	var hour		 sql.NullString
	var week                 sql.NullString
	var year		 sql.NullString

	var day_of_year		 sql.NullString
	var minute		 sql.NullString
	var second		 sql.NullString

	var month		 sql.NullString
	var day		         sql.NullString
	var shiftrange		 sql.NullString

	for rows.Next() {
		if err := rows.Scan(
		&id, 
		&scan_id,             
		&scan_moment,         
		&scan_source,         
		&sperscode,         
		&qualcode,            
		&ff_df,               
		&naheffing_hoogte,    
		&bgt_wegdeel,         
		&bgt_wegdeel_functie, 
		&buurtcode,           
		&buurtcombinatie,     
		&stadsdeel,           
		&parkeervak_id,       
		&parkeervak_soort,    
		&lat,	             
		&lon,		    

		&hour,		
		&week,    
		&year,	

		&day_of_year,	   
		&minute,		
		&second,

		&month,
		&day,

		&shiftrange,

		); err != nil {
			// Check for a scan error.
			// Query rows will be closed with defer.
			log.Fatal(err)
		}
		fmt.Println(lat)
		fmt.Println(lon)
		item := &Item{
			id:                   id,
			scan_id:              scan_id,
			scan_moment:          scan_moment,
			scan_source:          scan_source,
			sperscode:            sperscode,
			qualcode:	      qualcode,

			ff_df:		      ff_df,

			naheffing_hoogte:     naheffing_hoogte,
			bgt_wegdeel:          bgt_wegdeel,
			bgt_wegdeel_functie:  bgt_wegdeel_functie,
			buurtcode:            buurtcode,
			buurtcombinatie:      buurtcombinatie,
			stadsdeel:            stadsdeel,
			parkeervak_id:        parkeervak_id,
			lat:                  lat,
			lon:                  lon,

			hour:                 hour,
			week:                 week,
			year:                 year,

		        day_of_year:          day_of_year,
			minute:		      minute,
			second:               second,

			month:		     month,
			day:                 day,
			shiftrange:          shiftrange,
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
