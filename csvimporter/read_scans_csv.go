/*
	- Import scan csv data into postgres using copy streaming protocol
	- The database model should already be defined of the target table
	- clean csv lines
*/

package main

import (
	"database/sql"
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

//DatePair start and end data string values
type DatePair struct {
	start string
	end   string
}

var (
	csvError *log.Logger
	columns  []string
	success  int
	last     int
	workers  int
	failed   int

	//Db object we use all over the place
	Db *sql.DB

	//IdxMap columnname index mapping
	IdxMap       map[string]int
	resultTable  string
	targetTable  string
	targetCSVdir string
	wg           sync.WaitGroup
	start        time.Time

	//DateMap store per filename the start and end date
	DateMap map[string]DatePair
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

//timeTrack
func timeTrack(start time.Time, name string) {
	elapsed := time.Since(start)
	log.Printf("%s took %s", name, elapsed)
}

//create string to connect to database
func connectStr() string {

	otherParams := "sslmode=disable connect_timeout=5"
	return fmt.Sprintf(
		"user=%s dbname=%s password='%s' host=%s port=%s %s",
		"predictiveparking",
		"predictiveparking",
		"insecure",
		//"database",
		//"5432",
		"127.0.0.1",
		"5434",
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
		"scan_id",         //  ScanId;
		"scan_moment",     //  scnMoment;
		"device_id",       //  device id
		"scan_source",     //  scan_source;
		"longitude",       //  scnLongitude;
		"latitude",        //  scnLatitude;
		"buurtcode",       //  buurtcode;
		"afstand",         //  aftand to pvak?
		"sperscode",       //  spersCode;
		"qualcode",        //  qualCode;
		"ff_df",           //   FF_DF;
		"nha_nr",          //  NHA_nr;
		"nha_hoogte",      //  NHA_hoogte;
		"uitval_nachtrun", //  uitval_nachtrun;

		"stadsdeel",       //  stadsdeel;
		"buurtcombinatie", //  buurtcombinatie;
		"geometrie",       //  geometrie
	}

	IdxMap = make(map[string]int)
	DateMap = make(map[string]DatePair)

	resultTable = "metingen_scan"
	targetTable = "metingen_scanraw"
	//targetTable = "scans_scan"
	workers = 2
	ignoreErrors = false
	//TODO make environment variable
	targetCSVdir = "/app/unzipped"

	// fill map
	for i, field := range columns {
		IdxMap[field] = i
	}

	db, err := dbConnect(connectStr())
	Db = db

	checkErr(err)

}

//setLatLon create wgs84 point for postgres
func setLatLong(cols []interface{}) error {

	var long float64
	var lat float64
	var err error
	var point string

	if cols[IdxMap["longitude"]] == nil {
		return errors.New("longitude field value wrong")
	}

	if cols[IdxMap["latitude"]] == nil {
		return errors.New("latitude field value wrong")
	}

	if str, ok := cols[IdxMap["longitude"]].(string); ok {
		long, err = strconv.ParseFloat(str, 64)
	} else {
		return errors.New("longitude field value wrong")
	}

	if str, ok := cols[IdxMap["latitude"]].(string); ok {
		lat, err = strconv.ParseFloat(str, 64)
	} else {
		return errors.New("latitude field value wrong")
	}

	//bbox amsterdam
	//precision

	if err != nil {
		return err
	}

	point = geo.NewPointFromLatLng(lat, long).ToWKT()
	point = fmt.Sprintf("SRID=4326;%s", point)

	cols[IdxMap["geometrie"]] = point

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

		// normalize on dot notation
		cleanedField = strings.Replace(field, ",", ".", 1)
		cols[i] = cleanedField

		if i == IdxMap["buurtcode"] {
			cols[IdxMap["stadsdeel"]] = string(field[0])
			cols[IdxMap["buurtcombinatie"]] = field[:3]
		}

		//ignore afstand
		if i == IdxMap["afstand"] {
			cols[i] = ""
		}
	}

	err := setLatLong(cols)

	checkErr(err)

	if str, ok := cols[IdxMap["scan_id"]].(string); ok {
		if str == "" {
			return nil, errors.New("scan_id field missing")
		}
	} else {
		return nil, errors.New("scan_id field missing")
	}

	return cols, nil
}

func printRecord(record *[]string) {
	log.Println("\n source record:")
	for i, field := range *record {
		log.Printf("%2d %20s %32s", i, field, columns[i])
		csvError.Printf("%d %10s %22s", i, field, columns[i])
	}
}

func printCols(cols []interface{}) {
	log.Println("\ncolumns:")
	for i, field := range columns {
		log.Printf("%2d %20s %32s", i, field, cols[i])
	}
}

//csvloader streams one csv and commit into database
func csvloader(id int, jobs <-chan string) {

	fmt.Println("worker", id)

	for csvfile := range jobs {

		source, target := CreateTables(Db, csvfile)
		cleanTable(Db, target)
		cleanTable(Db, source)
		pgTable, err := NewImport(Db, "public", source, columns)
		checkErr(err)

		LoadSingleCSV(csvfile, pgTable)

		pgTable.Commit()
		// within 0.1 meter from parkeervak
		mergeScansParkeervakWegdelen(Db, source, target, 0.000001)
		// within 1.5 meters from parkeervak
		mergeScansParkeervakWegdelen(Db, source, target, 0.000015)

		mergeScansWegdelen(Db, source, target, 0.000001)

		// Drop import table
		//dropTargetTable(Db, source)
		// finalize csv file import in db
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

	files, err := filepath.Glob(fmt.Sprintf("%s/split*.csv", targetCSVdir))

	//fmt.Println(files)

	checkErr(err)

	if len(files) == 0 {
		fmt.Printf(targetCSVdir)
		panic(errors.New("Missing csv files"))
	}

	jobs := make(chan string, 500)

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

	CleanTargetTable(Db, targetTable)
	CleanTargetTable(Db, resultTable)

	importScans()

	fmt.Printf("csv loading done succes: %d failed: %d", success, failed)
}

//checkErr default crash hard error handling
func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
