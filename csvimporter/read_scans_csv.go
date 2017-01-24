/*
	- Import scan csv data into postgres using copy streaming protocol
	- The database model should already be defined of the target table
	- clean csv lines
	- when ignoreErrors skips invalid csv lines
*/

package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"path/filepath"
	//"net"
	"github.com/paulmach/go.geo"
	"strconv"
	"strings"
	"sync"
	"time"
)

var (
	csvError     *log.Logger
	columns      []string
	success      int
	last         int
	workers      int
	failed       int
	ignoreErrors bool
	targetTable  string
	targetCSVdir string
	wg           sync.WaitGroup
	start        time.Time
)

//set up logging..
func setLogging() {
	logfile, err := os.Create("csverrors.log")

	if err != nil {
		log.Fatalln("error opening file: %v", err)
	}

	//defer logfile.close()

	csvError = log.New(
		logfile,
		"CSV",
		log.Ldate|log.Ltime|log.Lshortfile)

	csvError.Println("csv loading started...")
}

//create string to connect to database
func connectStr() string {

	otherParams := "sslmode=disable connect_timeout=5"
	return fmt.Sprintf(
		"user=%s dbname=%s password='%s' host=%s port=%s %s",
		"predictiveparking",
		"predictiveparking",
		"insecure",
		"database",
		"5432",
		//"127.0.0.1",
		//"5434",
		otherParams,
	)
}

/*
Example csv row

ScanId;scnMoment;scan_source;scnLongitude;scnLatitude;buurtcode;afstand;spersCode;qualCode;FF_DF;NHA_nr;NHA_hoogte;uitval_nachtrun
149018849;2016-11-21 00:07:58;SCANCAR;4.9030151;52.375652;A04d;Distance:13.83;Skipped;DISTANCE;;;0;
*/

func init() {
	columns = []string{
		"scan_id",         // 0  ScanId;
		"scan_moment",     // 1  scnMoment;
		"scan_source",     // 2  scan_source;
		"longitude",       // 3  scnLongitude;
		"latitude",        // 4  scnLatitude;
		"buurtcode",       // 5  buurtcode;
		"afstand",         // 6  aftand to pvak?
		"sperscode",       // 7  spersCode;
		"qualcode",        // 8  qualCode;
		"ff_df",           // 9  FF_DF;
		"nha_nr",          // 10 NHA_nr;
		"nha_hoogte",      // 11 NHA_hoogte;
		"uitval_nachtrun", // 12 uitval_nachtrun;

		"stadsdeel",       // 13  stadsdeel;
		"buurtcombinatie", // 14  buurtcombinatie;
		"geometrie",       // 15 geometrie
	}

	targetTable = "scans_scan"
	workers = 3
	ignoreErrors = false
	//TODO make environment variable
	targetCSVdir = "/tmp/unzipped"
}

//setLatLon create wgs84 point for postgres
func setLatLong(cols []interface{}) error {

	var long float64
	var lat float64
	var err error
	var point string

	if str, ok := cols[3].(string); ok {
		long, err = strconv.ParseFloat(str, 64)
	} else {
		return errors.New("long field value wrong")
	}

	if str, ok := cols[4].(string); ok {
		lat, err = strconv.ParseFloat(str, 64)
	} else {
		return errors.New("lat field value wrong")
	}

	if err != nil {
		return err
	}

	point = geo.NewPointFromLatLng(lat, long).ToWKT()
	point = fmt.Sprintf("SRID=4326;%s", point)
	cols[15] = point

	return nil

}

//NormalizeRow cleanup fields in csv we recieve a single row
func NormalizeRow(record *[]string) ([]interface{}, error) {

	cols := make([]interface{}, len(columns))

	cleanedField := ""

	for i, field := range *record {
		if field == "" {
			continue
		}

		cleanedField = strings.Replace(field, ",", ".", 1)
		cols[i] = cleanedField

		if i == 5 {
			cols[13] = string(field[0]) //stadsdeel
			cols[14] = field[:3]        //buurtcombinatie
		}
	}

	if cols[8] == "Distanceerror" {
		return nil, errors.New("Distanceerror in 'afstand'")
	}

	err := setLatLong(cols)

	if err != nil {
		return nil, err
	}

	if err != nil {
		//not a valid point
		return nil, errors.New("invalid lat long")
	}

	return cols, nil
}

func printRecord(record *[]string) {
	log.Println("\n source record:")
	for i, field := range *record {
		log.Println(columns[i], field)
		csvError.Printf("%10s %s", field, columns[i])
	}
}

func printCols(cols []interface{}) {
	log.Println("\ncolumns:")
	for i, field := range columns {
		log.Printf("%10s %s", field, cols[i])
	}
}

func csvloader(id int, jobs <-chan string) {

	fmt.Println("worker", id)

	for csvfile := range jobs {

		db, err := dbConnect(connectStr())

		if err != nil {
			log.Fatalln(err)
		}

		pgTable, err := NewImport(
			db, "public", "scans_scan", columns)

		LoadSingleCSV(csvfile, pgTable)
		//finalize csv file import in db
		pgTable.Commit()

	}
	fmt.Println("Done", id)
	defer wg.Done()
}

func printStatus() {
	for {
		time.Sleep(1 * time.Second)
		fmt.Printf(
			"\r STATUS: %10d:imported %10d:failed  %10d rows/s",
			success, failed, success-last)
		last = success
	}
}

//importScans find all csv file with scans to import
func importScans() {

	//Gives docker time to print output
	time.Sleep(3 * time.Second)
	//find all csv files
	start := time.Now()

	files, err := filepath.Glob(fmt.Sprintf("%s/*week*.csv", targetCSVdir))

	if err != nil {
		panic(err)
	}

	if len(files) == 0 {
		panic(errors.New("Missing csv files"))
	}

	jobs := make(chan string, 100)

	for _, file := range files {
		jobs <- file
	}
	close(jobs)

	go printStatus()

	for w := 1; w <= workers; w++ {
		wg.Add(1)
		go csvloader(w, jobs)
	}

	wg.Wait()
	fmt.Println("\n Duration:", time.Now().Sub(start))

}

func main() {
	fmt.Println("Reading scans..")

	setLogging()

	// CleanTargetTable(db, targetTable)

	importScans()

	fmt.Printf("csv loading done succes: %d failed: %d", success, failed)
}
