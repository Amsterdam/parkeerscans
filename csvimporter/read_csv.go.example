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
	"strings"
	//"time"
)

var (
	csvError     *log.Logger
	columns      []string
	success      int
	failed       int
	ignoreErrors bool
	targetTable  string
	targetCSVdir string
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
		"scan_id",         // 0  ScanId;
		"scan_moment",     // 1  scnMoment;
		"scan_source",     // 2  scan_source;
		"longitude",       // 3  buurtcode;
		"latitude",        // 4  scnLatitude;
		"buurtcode",       // 5  afstand;
		"afstand",         // 6  scnLongitude;
		"sperscode",       // 7  spersCode;
		"qualcode",        // 8  qualCode;
		"ff_df",           // 9  FF_DF;
		"nha_nr",          // 10 NHA_nr;
		"nha_hoogte",      // 11 NHA_hoogte;
		"uitval_nachtrun", // 12 uitval_nachtrun;
	}

	targetTable = "scans_scan"
	success = 0
	ignoreErrors = false
	//TODO make environment variable
	targetCSVdir = "/home/stephan/work/predictive_parking/web/predictive_parking/unzipped"
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

	}

	if cols[6] == "Distanceerror" {
		return nil, errors.New("Distanceerror in 'afstand'")
	}

	return cols, nil
}

func printRecord(record *[]string) {
	for i, field := range *record {
		log.Println(columns[i], field)
		csvError.Println(columns[i], field)
	}
}

//importScans find all csv file with scans to import
func importScans(pgTable *SQLImport) {

	//find all csv files

	files, err := filepath.Glob(fmt.Sprintf("%s/*week*.csv", targetCSVdir))
	if err != nil {
		panic(err)
	}

	for _, file := range files {
		LoadSingleCSV(file, pgTable)
	}

	//finalize import in db
	pgTable.Commit()

}

func main() {
	fmt.Println("Reading scans..")

	setLogging()

	db, err := dbConnect(connectStr())

	if err != nil {
		log.Fatalln(err)
	}

	CleanTargetTable(db, targetTable)

	importTarget, err := NewImport(
		db, "public", "scans_scan", columns)

	importScans(importTarget)

	fmt.Printf("csv loading done succes: %d failed: %d", success, failed)
}
