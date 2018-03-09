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
	"sort"
	//"net"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/paulmach/go.geo"
)

//DatePair start and end data string values
type DatePair struct {
	start string
	end   string
}

type fileErrorMap map[string]int

var (
	csvError *log.Logger
	// columns  []string
	success int
	indb    int
	last    int
	workers int
	failed  int

	//Db object we use all over the place
	Db *sql.DB

	//idxMap columnname index mapping
	// idxMap     map[string]int
	fieldMap2016 map[string]int
	fieldMap22   map[string]int
	fieldMap23   map[string]int
	dbFieldMap   map[string]int
	//track errors
	fileErrorsMap fileErrorMap
	targetCSVdir  string
	wg            sync.WaitGroup
	start         time.Time

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
Example csv row (OLD)

ScanId     scnMoment            device_id  scan_source  scnLongitude  scnLatitude  buurtcode       afstand  spersCode  qualCode  FF_DF  NHA_nr  NHA_hoogte  uitval_nachtrun
149018849  2016-11-21 00:07:58  SCANCAR    4.9030151    52.375652     A04d         Distance:13.83  Skipped  DISTANCE   0

*/

/*

Example csv row (NEW)

ScanId     scnMoment            device_id  scan_source  scnLongitude        scnLatitude         buurtcode  afstand        spersCode  qualCode  FF_DF  NHA_nr  NHA_hoogte  uitval_nachtrun  DistanceToParkingBay  GPS_Vehicle  GPS_PLate  GPS_ScanDevice  location_ParkingBay  ParkingBay_angle  Reliability_GPS  Reliability_ANPR
202075788  2017-10-30 00:00:01  299        SCANCAR      4.9025221859999997  52.371931009999997  A04E       PermittedPRDB  BEWONERP   0

*/

func init() {

	fieldMap22 = makeIndexMapping(columns22)
	fieldMap23 = makeIndexMapping(columns23)
	fieldMap2016 = makeIndexMapping(columns2016)
	dbFieldMap = makeIndexMapping(dbColumns)

	DateMap = make(map[string]DatePair)
	fileErrorsMap = make(fileErrorMap)
	success = 1
	indb = 0

	workers = 3

	//TODO make environment variable
	targetCSVdir = "/app/unzipped"

	db, err := dbConnect(ConnectStr())
	Db = db

	checkErr(err)

}

func (d fileErrorMap) SetDefault(key string, val int) (result int) {
	if v, ok := d[key]; ok {
		return v
	}
	d[key] = val
	return val
}

//setLatLon create wgs84 point for postgres
func setLatLong(cols []interface{}, fieldMap map[string]int) error {

	var long float64
	var lat float64
	var err error
	var point string

	if cols[fieldMap["longitude"]] == nil {
		return errors.New("longitude field value wrong")
	}

	if cols[fieldMap["latitude"]] == nil {
		return errors.New("latitude field value wrong")
	}

	if str, ok := cols[fieldMap["longitude"]].(string); ok {
		long, err = strconv.ParseFloat(str, 64)
	} else {
		return errors.New("longitude field value wrong")
	}

	if str, ok := cols[fieldMap["latitude"]].(string); ok {
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

	cols[fieldMap["geometrie"]] = point

	return nil

}

//parseReliabilityGPS check gps value of another field in csv..
func parseReliabilityGPS(gpsfield string, cols []interface{}, fieldMap map[string]int) error {
	var long float64
	var lat float64
	var err error
	var point string

	//lat           long
	//52.356895123N.4.849403218E
	splitVal := strings.Split(gpsfield, ",")
	splitN := strings.Split(splitVal[0], "N")[0]
	splitE := splitVal[1]
	splitE = strings.Split(splitE, "E")[0]

	long, err = strconv.ParseFloat(splitN, 64)
	if err != nil {
		return errors.New("gps reliability latitude field value wrong")
	}

	lat, err = strconv.ParseFloat(splitE, 64)
	if err != nil {
		return errors.New("gps reliability longitude field value wrong")
	}

	point = geo.NewPointFromLatLng(lat, long).ToWKT()
	point = fmt.Sprintf("SRID=4326;%s", point)

	cols[fieldMap["reliability_gps"]] = point

	return nil
}

func cleanBuurtCode(buurt string, cols []interface{}, fieldMap map[string]int) {

	size := len(buurt)
	if size > 0 && size < 5 {
		cols[fieldMap["stadsdeel"]] = string(buurt[0])
		cols[fieldMap["buurtcombinatie"]] = buurt[:3]
	} else {

		cols[fieldMap["buurtcode"]] = ""
	}
}

func cleanupRow(
	record *[]string,
	row []interface{},
	fieldMap map[string]int, countErrors int) int {

	cleanedField := ""

	for i, field := range *record {
		if field == "" {
			continue
		}

		// normalize all fields on dot notation
		cleanedField = strings.Replace(field, ",", ".", 1)

		row[i] = cleanedField

		if i == fieldMap["buurtcode"] {
			cleanBuurtCode(field, row, fieldMap)
			continue
		}

		if val, ok := fieldMap["reliability_gps"]; ok {
			if i == val {
				err := parseReliabilityGPS(field, row, fieldMap)
				if err != nil {
					countErrors++
				}
				continue
			}
		}

		// parse afstand
		if val, ok := fieldMap["reliability_gps"]; ok {
			if i == val {
				parsedFloat, err := strconv.ParseFloat(field, 64)
				if err != nil {
					row[i] = ""
					countErrors++
				} else {
					row[i] = parsedFloat
				}
			}
		}

	}
	return countErrors
}

func floatToString(inputNum float64) string {
	// to convert a float number to a string
	return strconv.FormatFloat(inputNum, 'f', 0, 64)
}

//NormalizeRow cleanup fields in csv we return a single database ready row
func NormalizeRow(record *[]string) ([]interface{}, int, error) {

	countErrors := 0

	fieldMap := make(map[string]int)
	dbCols := make([]interface{}, len(dbColumns))
	// we take the longest array
	row := make([]interface{}, len(columns23))
	fieldnames := columns22

	// figure out which mapping we need to use for cvs record
	if len(*record) == 22 {
		fieldMap = fieldMap22
	} else if len(*record) == 23 {
		fieldnames = columns23
		fieldMap = fieldMap23
	} else if len(*record) == 14 {
		fieldnames = columns2016
		fieldMap = fieldMap2016
	}

	countErrors = cleanupRow(record, row, fieldMap, countErrors)

	err := setLatLong(row, fieldMap)

	//validate record
	if err != nil {
		//printRecord(record, row)
		//printCols(row, fieldnames)
		countErrors++

		return nil, countErrors, errors.New("lat long field failure")
	}

	scanID := row[fieldMap["scan_id"]]

	if str, ok := scanID.(string); ok {
		if str == "" {
			countErrors++
			return nil, countErrors, errors.New("scan_id field empty")
		}
	} else if flt, ok := scanID.(float64); ok {
		scanID = floatToString(flt)
	} else {
		log.Println(row[fieldMap["scan_id"]])
		countErrors++
		printCols(row, fieldnames)
		log.Println(len(fieldMap))
		panic(str)
		//return nil, countErrors, errors.New("scan_id not valid")
	}

	stadsdeel := row[fieldMap["stadsdeel"]]
	if str, ok := stadsdeel.(string); ok {
		if len(str) > 1 {
			printCols(row, fieldnames)
			panic("stadsdeel wrong")
		}
	}

	row[fieldMap["scan_id"]] = scanID

	// copy fields to database columns ready row
	for i, field := range fieldnames {
		if idx, ok := dbFieldMap[field]; ok {
			dbCols[idx] = row[i]
		}
	}

	return dbCols, countErrors, nil
}

func printRecord(record *[]string, columns []interface{}) {
	log.Println("\n source record:")
	for i, field := range *record {
		log.Printf("%2d %20s %32s", i, field, columns[i])
		csvError.Printf("%d %10s %22s", i, field, columns[i])
	}
}

func printCols(cols []interface{}, target []string) {
	log.Println("\ncolumns:")
	for i, field := range target {
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

		pgTable, err := NewImport(Db, "public", source, dbColumns)
		checkErr(err)

		LoadSingleCSV(csvfile, pgTable)

		err = pgTable.Commit()
		if err != nil {
			//panic(err)
		}
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

	var keys []string
	for k := range fileErrorsMap {
		keys = append(keys, k)
	}

	sort.Strings(keys)

	v := 0

	for _, k := range keys {
		v = fileErrorsMap[k]
		parts := strings.Split(k, "/")
		filename := parts[len(parts)-1]
		log.Println(filename, v)
	}
}

//checkErr default crash hard error handling
func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
