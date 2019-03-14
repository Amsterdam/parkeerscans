package main

import (
	"database/sql"
	"fmt"
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
