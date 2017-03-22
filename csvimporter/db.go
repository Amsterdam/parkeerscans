package main

import (
	"database/sql"
	"encoding/csv"
	"errors"
	"fmt"
	"regexp"
	//"github.com/cheggaaa/pb"
	"github.com/lib/pq"
	"io"
	"log"
	"os"
	"strings"
	"time"
)

//SQLImport import structure
type SQLImport struct {
	txn  *sql.Tx
	stmt *sql.Stmt
}

//AddRow Add a single row of data to the database
func (i *SQLImport) AddRow(columns ...interface{}) error {
	_, err := i.stmt.Exec(columns...)
	return err
}

//Commit the import to database
func (i *SQLImport) Commit() error {

	_, err := i.stmt.Exec()
	if err != nil {
		return err
	}

	// Statement might already be closed
	// therefore ignore errors
	_ = i.stmt.Close()

	return i.txn.Commit()
}

//CleanTargetTable the table we are importing to
func cleanTable(db *sql.DB, target string) {

	sql := fmt.Sprintf("TRUNCATE TABLE %s;", target)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}
}

//dropTargetTable drop it!
func dropTargetTable(db *sql.DB, target string) {

	sql := fmt.Sprintf("DROP TABLE IF EXISTS %s;", target)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

}

// add vakken / wegdelen to scans

//NewImport setup a new import struct
func NewImport(db *sql.DB, schema string, tableName string, columns []string) (*SQLImport, error) {

	txn, err := db.Begin()

	if err != nil {
		return nil, err
	}

	stmt, err := txn.Prepare(pq.CopyInSchema(schema, tableName, columns...))
	if err != nil {
		return nil, err
	}

	return &SQLImport{txn, stmt}, nil
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

// NewProgressBar initializes new progress bar based on size of file
//func NewProgressBar(file *os.File) *pb.ProgressBar {
//	fi, err := file.Stat()
//
//	total := int64(0)
//	if err == nil {
//		total = fi.Size()
//	}
//
//	bar := pb.New64(total)
//	bar.SetUnits(pb.U_BYTES)
//	return bar
//}

//LoadSingleCSV import single csv file into  database with progresbar
func LoadSingleCSV(filename string, pgTable *SQLImport) DatePair {

	//var bar *pb.ProgressBar
	// load file
	csvfile, err := os.Open(filename)
	defer csvfile.Close()

	//bar = NewProgressBar(csvfile)

	if err != nil {
		log.Println(err)
		panic(err)
	}

	//reader := csv.NewReader(io.TeeReader(csvfile, bar))
	reader := csv.NewReader(csvfile)
	//bar.Start()
	//stream contents of csv into postgres
	startDate, endDate := importCSV(pgTable, reader)
	if startDate.After(endDate) {
		panic("Dates wrong!")
	}
	//bar.Finish()
	startEnd := DatePair{}
	format := "2006-01-02"
	startEnd.start = startDate.Format(format)
	startEnd.end = endDate.Format(format)
	//update DateMap
	//DateMap[filename] = startEnd
	log.Printf("Batch: %s %s < %s", filename, startEnd.start, startEnd.end)
	return startEnd
}

//procesDate update startDate and endDate
func procesDate(cols []interface{},
	startDate time.Time, endDate time.Time) (time.Time, time.Time, error) {

	//2016-04-11 09:11:2
	type timetest string

	if str, ok := cols[IdxMap["scan_moment"]].(string); ok {
		timetest, err := time.Parse("2006-01-02 15:04:05", str)

		if err != nil {
			return startDate, endDate, errors.New("date string wrong")
		}

		if timetest.After(endDate) {
			endDate = timetest
		} else if timetest.Before(startDate) {
			startDate = timetest
		}

	} else {
		return startDate, endDate, errors.New("date string wrong")
	}

	return startDate, endDate, nil
}

//CreateTables  table to put csv data in
func CreateTables(db *sql.DB, csvfile string) (string, string) {

	validTableName := regexp.MustCompile("201([a-z_0-9]*)")

	tableName := validTableName.FindString(csvfile)

	if tableName == "" {
		panic(errors.New("filename no regexmatch"))
	}

	targetTable := fmt.Sprintf("scans_%s", tableName)
	importTable := fmt.Sprintf("import_%s", tableName)

	log.Println("Tablename", targetTable)

	makeTable(db, targetTable)
	makeTable(db, importTable)

	return importTable, targetTable

}

func makeTable(db *sql.DB, tableName string) {

	sql := fmt.Sprintf(`CREATE UNLOGGED TABLE IF NOT EXISTS %s (
		LIKE metingen_scanraw
		);`, tableName)

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}

	sql = fmt.Sprintf(`ALTER TABLE %s DROP COLUMN id;`, tableName)

	if _, err := db.Exec(sql); err != nil {
		log.Println("Tablename already there", tableName)
	}

}

func importCSV(pgTable *SQLImport, reader *csv.Reader) (time.Time, time.Time) {

	reader.FieldsPerRecord = 0
	reader.Comma = ';'
	//Ignore first header line
	_, err := reader.Read()

	if err != nil {
		panic(err)
	}

	startDate := time.Now()
	endDate := time.Now().AddDate(-3, 0, 0)

	delimiter := ";"
	rowCount := 0

	for {
		record, err := reader.Read()

		if err == io.EOF {
			break
		}

		if err != nil {
			csvError.Printf("%s: %s \n", err, record)
			failed++
			continue
		}

		rowCount++

		cols, err := NormalizeRow(&record)

		if err != nil {
			log.Println(err)
			csvError.Printf("%s: %s \n", err, record)
			failed++
			continue
		}

		//printRecord(&record)
		//printCols(cols)
		//Determine startDate / endDate in stream
		startDate, endDate, err = procesDate(cols, startDate, endDate)

		if err != nil {
			failed++
			continue
		}

		err = pgTable.AddRow(cols...)

		if err != nil {
			line := strings.Join(record, delimiter)
			err = fmt.Errorf("%s: %s", err, line)
			printRecord(&record)
			printCols(cols)
			panic(err)
		}
		success++

	}

	return startDate, endDate
}
