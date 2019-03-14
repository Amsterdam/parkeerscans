package main

import (
	"log"
	"net/http"
	"sync"
	"time"

	// elastic retries

	"gopkg.in/olivere/elastic.v6"
)

// globals
var client *elastic.Client
var wg sync.WaitGroup
var mapRows int

// AllScans will container all scans in memory
var AllScans theList
var wegdelen map[string]*wegdeel

type filterFunc func() []*Scan

type theList []*Scan
type groupByType map[string]theList

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

	// elastic search settings
	SETTINGS.Set("file", "mappings.json", "Path to file with elastic search mapping")
	SETTINGS.Set("index", "not-set", "Name of the Elastic Search Index")
	SETTINGS.Set("eshost", "elasticsearch", "Specify Elastic search Host")
	SETTINGS.SetInt("esport", 9200, "Specify elastic search port")
	SETTINGS.SetInt("esbuffer", 1000, "Buffer items before sending to elasticsearch")

	SETTINGS.Parse()
	mapRows = 0

	AllScans = make(theList, 100000)
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

	// this should go rest service.
	aEndResult := fillWegDeelVakkenByHour()

	http.HandleFunc("/", rest)
	log.Fatal(http.ListenAndServe("0:8080", nil))
}

func mapKey(item *Scan) string {
	t := time.Unix(item.Scan_moment, 0)
	keylayout := "2006-01-02T15"
	return t.Format(keylayout)
}

func worker(workID int, chItems chan *Scan) {

	for scan := range chItems {

		mapRows++
		//pvmap.
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
