package main

import (
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

// globals
var wg sync.WaitGroup
var mapRows int

// AllScans will container all scans in memory
var AllScans Scans
var wegdelen map[string]*wegdeel

type filterFunc func() []*Scan
type groupByType map[string]Scans

func init() {
	// run settings
	SETTINGS.SetInt("workers", 4, "Specify mount of workers")
	SETTINGS.SetInt("monthsago", 1, "start from minus month x from now")

	// postgres settings
	SETTINGS.Set("dbhost", "database", "Specify Elastic search Host")
	SETTINGS.Set("dbpwsd", "insecure", "Set Database Password")
	SETTINGS.Set("dbname", "parkeerscans", "Set database name")
	SETTINGS.Set("dbuser", "user", "Set database user")
	SETTINGS.SetInt("dbport", 5432, "Specify database port")

	SETTINGS.Set("storefile", "storage.json", "Specify name for file, that stores scans")

	SETTINGS.Parse()
	mapRows = 0

	AllScans = Scans{}
	wegdelen = make(map[string]*wegdeel, 10000)
}

func main() {
	//var err error

	// start workers
	chItems := make(chan *Scan, 100000)
	workers := SETTINGS.GetInt("workers")

	go printStatus(chItems)

	wg.Add(workers)

	for i := 0; i < workers; i++ {
		go worker(i, chItems)
	}

	fillWegdelenFromDB()
	fillScansFromDB(chItems)
	close(chItems)
	wg.Wait()

	go runPrintMem()
	// Runserver rest serivice
	http.HandleFunc("/", listRest)
	http.HandleFunc("/help/", helpRest)
	http.HandleFunc("/load/", func(w http.ResponseWriter, r *http.Request) { loadFile() })
	fmt.Println("starting server, with:", len(AllScans), "items")
	log.Fatal(http.ListenAndServe("0:8080", nil))
}

func mapKey(item *Scan) string {
	keylayout := "2006-01-02T15"
	return item.ScanMoment.Format(keylayout)
}

func worker(workID int, chItems chan *Scan) {
	for scan := range chItems {
		mapRows++
		AllScans = append(AllScans, scan)

	}
	wg.Done()
}

func printStatus(chItems chan *Scan) {
	i := 1
	delta := 5
	duration := 0
	speed := 0
	lastRowCount := -1

	for {
		time.Sleep(time.Duration(delta) * time.Second)

		if mapRows == lastRowCount {
			log.Printf("Done loading scans from DB")
			break
		}

		log.Printf("STATUS: rows:%-10d  %-10d rows/sec  buffer: %d", mapRows, speed, len(chItems))
		duration = i * delta
		speed = mapRows / duration
		i++

		lastRowCount = mapRows
	}
}
