package main

import (
	"database/sql"
	//"errors"
	"fmt"
	//"github.com/lib/pq"
	//"github.com/paulmach/go.geo"
	elastic "gopkg.in/olivere/elastic.v5"
	"time"
)

//ConnectStr create string to connect to database
func ConnectStr() string {

	otherParams := "sslmode=disable connect_timeout=5"
	return fmt.Sprintf(
		"user=%s dbname=%s password='%s' host=%s port=%s %s",
		"predictiveparking",
		"predictiveparking",
		"insecure",
		"database",
		"5432",
		otherParams,
	)
}

//setup a database connection
func dbConnect(connStr string) (*sql.DB, error) {
	//connStr := connectStr()
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return db, err
	}

	err = db.Ping()
	if err != nil {
		return db, err
	}

	return db, nil
}

//TODO:
//determine table name from argument
//detemine count.
//devide in batch jobs.
//index scans in jobs

func makeScanDoc(row *sql.Rows) (string, Scan) {
	var ID int
	var scanID string
	var moment time.Time
	var scanSource string
	var deviceID string

	var qualcode sql.NullString
	var sperscode sql.NullString

	var parkeervakID sql.NullString
	var parkeervakSoort sql.NullString

	var BGTwegdeel sql.NullString
	var BGTwegdeelFunctie sql.NullString

	var nhaHoogte sql.NullFloat64
	var ffdf sql.NullString

	var lat float64
	var lon float64

	err := row.Scan(
		&ID,
		&scanID,
		&moment,
		&scanSource,
		&deviceID,

		&qualcode,
		&sperscode,

		&parkeervakID,
		&parkeervakSoort,

		&BGTwegdeel,
		&BGTwegdeelFunctie,

		&nhaHoogte,
		&ffdf,

		&lat,
		&lon,
	)

	panicOnErr(err)

	scan := Scan{
		ID:         fmt.Sprintf("%d-%s", ID, scanID),
		DeviceID:   deviceID,
		ScanSource: scanSource,

		//Qualcode:   qualcode,
		//Sperscode:  sperscode,
		ScanMoment: moment,
		Minute:     moment.Minute(),
		Second:     moment.Second(),
		Hour:       moment.Hour(),
		Day:        moment.Weekday().String(),
		Month:      moment.Month().String(),
		DayOfYear:  moment.YearDay(),
		Year:       moment.Year(),

		Geo: elastic.GeoPoint{Lat: lat, Lon: lon},
	}

	if qualcode.Valid {
		scan.Qualcode = qualcode.String
	}

	if sperscode.Valid {
		scan.Sperscode = sperscode.String
	}
	if nhaHoogte.Valid {
		scan.NHAHoogte = nhaHoogte.Float64
	}

	if BGTwegdeel.Valid {
		scan.BGTwegdeel = BGTwegdeel.String
	}

	if BGTwegdeelFunctie.Valid {
		scan.BGTwegdeelFunctie = BGTwegdeel.String
	}
	return moment.Format("2006-01-02"), scan
}

func fetchScans(jsonscans chan momentScan) {

	scansql := fmt.Sprintf(`
	SELECT  id,
		scan_id,
		scan_moment,
		scan_source,
		device_id,

		qualcode,
		sperscode,

		parkeervak_id,
		parkeervak_soort,

		bgt_wegdeel,
		bgt_wegdeel_functie,

		nha_hoogte,
		ff_df,

		round(ST_Y(geometrie)::numeric,8) as lat,
		round(ST_X(geometrie)::numeric,8) as lon

	FROM metingen_scan limit 1000
	`)

	rows, err := Db.Query(scansql)

	panicOnErr(err)

	for rows.Next() {

		date, scan := makeScanDoc(rows)

		fmt.Println(scan)
		fmt.Printf("\nscans-%s\n", date)

		mscan := momentScan{
			scan:  scan,
			index: date,
		}

		jsonscans <- mscan
	}

	defer wg.Done()
	close(jsonscans)
}
