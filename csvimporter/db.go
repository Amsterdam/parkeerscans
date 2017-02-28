package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	//"github.com/cheggaaa/pb"
	"github.com/lib/pq"
	"io"
	"os"
	"strings"
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
func CleanTargetTable(db *sql.DB, target string) {

	if _, err := db.Exec(`TRUNCATE TABLE scans_scan`); err != nil {
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
func LoadSingleCSV(filename string, pgTable *SQLImport) {

	//var bar *pb.ProgressBar
	// load file
	csvfile, err := os.Open(filename)
	defer csvfile.Close()

	//bar = NewProgressBar(csvfile)

	if err != nil {
		fmt.Println(err)
		panic(err)
	}

	msg := fmt.Sprintf("\nReading %s", filename)
	fmt.Println(msg)
	csvError.Println(msg)

	//reader := csv.NewReader(io.TeeReader(csvfile, bar))
	reader := csv.NewReader(csvfile)
	//bar.Start()
	//stream contents of csv into postgres
	importCSV(pgTable, reader)
	//bar.Finish()
}

func importCSV(pgTable *SQLImport, reader *csv.Reader) error {

	reader.FieldsPerRecord = 0
	reader.Comma = ';'
	//Ignore first header line
	_, err := reader.Read()
	if err != nil {
		panic(err)
	}

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
			fmt.Println(err)
			csvError.Printf("%s: %s \n", err, record)
			failed++
			continue
		}

		//printRecord(&record)
		//printCols(cols)

		err = pgTable.AddRow(cols...)

		if err != nil {
			line := strings.Join(record, delimiter)

			failed++

			if ignoreErrors {
				csvError.Println(string(line))
				continue
			} else {
				err = fmt.Errorf("%s: %s", err, line)
				printRecord(&record)
				printCols(cols)
				panic(err)
			}
		}

		success++

	}

	return nil
}
