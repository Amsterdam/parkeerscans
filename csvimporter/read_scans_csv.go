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
	indb     int
	last     int
	workers  int
	failed   int

	//Db object we use all over the place
	Db *sql.DB

	//idxMap columnname index mapping
	idxMap       map[string]int
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

	idxMap = make(map[string]int)
	DateMap = make(map[string]DatePair)
	success = 1
	indb = 0

	workers = 3

	//TODO make environment variable
	targetCSVdir = "/app/unzipped"

	// fill map
	for i, field := range columns {
		idxMap[field] = i
	}

	db, err := dbConnect(ConnectStr())
	Db = db

	checkErr(err)

}

//setLatLon create wgs84 point for postgres
func setLatLong(cols []interface{}) error {

	var long float64
	var lat float64
	var err error
	var point string

	if cols[idxMap["longitude"]] == nil {
		return errors.New("longitude field value wrong")
	}

	if cols[idxMap["latitude"]] == nil {
		return errors.New("latitude field value wrong")
	}

	if str, ok := cols[idxMap["longitude"]].(string); ok {
		long, err = strconv.ParseFloat(str, 64)
	} else {
		return errors.New("longitude field value wrong")
	}

	if str, ok := cols[idxMap["latitude"]].(string); ok {
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

	cols[idxMap["geometrie"]] = point

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

		if i == idxMap["buurtcode"] {
			cols[idxMap["stadsdeel"]] = string(field[0])
			cols[idxMap["buurtcombinatie"]] = field[:3]
		}

		//ignore afstand
		if i == idxMap["afstand"] {
			cols[i] = ""
		}
	}

	err := setLatLong(cols)

	if err != nil {
		printRecord(record)
		printCols(cols)
		panic(err)
		//return nil, errors.New("lat long field failure")
	}

	if str, ok := cols[idxMap["scan_id"]].(string); ok {
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

	log.Print("worker", id)

	for csvfile := range jobs {

		source, target := CreateTables(Db, csvfile)

		cleanTable(Db, target)
		cleanTable(Db, source)

		pgTable, err := NewImport(Db, "public", source, columns)
		checkErr(err)

		LoadSingleCSV(csvfile, pgTable)

		pgTable.Commit()
		// within 0.1 meter from parkeervak
		count1 := mergeScansParkeervakWegdelen(Db, source, target, 0.000001)
		// within 1.5 meters from parkeervak
		count15 := mergeScansParkeervakWegdelen(Db, source, target, 0.000015)
		// scans op bgt wegdeel
		countW := mergeScansWegdelen(Db, source, target, 0.000001)

		indb += countW

		log.Printf("\n\n%s pv 0.1m:%d  pv1.5m:%d  w:%d \n\n",
			target,
			count1, count15, countW,
		)
		// Drop import table
		dropTable(Db, source)
		// finalize csv file import in db
	}
	log.Print("Done:", id)
	defer wg.Done()
}

func printStatus() {
	i := 1
	delta := 10
	duration := 0
	speed := 0

	for {
		time.Sleep(time.Duration(delta) * time.Second)

		countT := totalProcessedScans(Db)

		log.Printf("STATUS: rows:%-10ds inDB: %-10d failed %-10d  - %10d rows/s  %10d Total",
			success, indb, failed, speed, countT)
		duration = i * delta
		speed = success / duration
		i++
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
		log.Printf(targetCSVdir)
		panic(errors.New("Missing csv files"))
	}

	jobs := make(chan string, 500)

	for _, file := range files {
		log.Println(file)
		jobs <- file
	}

	close(jobs)

	go printStatus()

	for w := 1; w <= workers; w++ {
		wg.Add(1)
		go csvloader(w, jobs)
	}

	wg.Wait()

	log.Print("\n Duration:", time.Now().Sub(start))

}

func main() {
	log.Print("Importing scans..")

	setLogging()

	importScans()

	log.Printf("COUNTS: rows:%-10ds inDB: %-10d failed %-10d", success, indb, failed)

}

//checkErr default crash hard error handling
func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
