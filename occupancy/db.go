package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"strconv"
)

//ConnectStr create string to connect to database
func ConnectStr() string {

	otherParams := "sslmode=disable connect_timeout=5"
	return fmt.Sprintf(
		"user=%s dbname=%s password='%s' host=%s port=%d %s",
		"parkeerscans",
		"parkeerscans",
		"insecure",
		SETTINGS.Get("dbhost"),
		SETTINGS.GetInt("dbport"),
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

func convertSqlNullString(v sql.NullString) string {
	var err error
	var raw []byte

	if v.Valid {
		raw, err = json.Marshal(v.String)
	} else {
		raw, err = json.Marshal(nil)
	}

	if err != nil {
		panic(err)
	}

	noquotes := string(raw[1 : len(raw)-1])
	return noquotes

}

func convertSqlNullInt(v sql.NullInt64) int64 {
	var err error
	var output []byte

	if v.Valid {
		output, err = json.Marshal(v.Int64)
	} else {
		output, err = json.Marshal(nil)
		return int64(0)
	}

	if err != nil {
		panic(err)
	}

	bla, err := strconv.ParseInt(string(output), 10, 64)

	if err != nil {
		panic(err)
	}

	return bla

}

func convertSqlNullFloat(v sql.NullFloat64) float64 {
	var err error
	var output []byte

	if v.Valid {
		output, err = json.Marshal(v.Float64)
	} else {
		output, err = json.Marshal(nil)
		return float64(0)
	}

	if err != nil {
		panic(err)
	}

	bla, err := strconv.ParseFloat(string(output), 64)

	if err != nil {
		panic(err)
	}

	return bla

}
