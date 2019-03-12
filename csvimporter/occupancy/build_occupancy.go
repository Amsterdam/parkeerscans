package main

import (
	"log"
	"strings"
	"sync"
	"time"

	// elastic retries

	"gopkg.in/olivere/elastic.v6"
)

// globals
var client *elastic.Client
var wg sync.WaitGroup
var mapRows int
var monsterMap MonsterMap

type WegDeelStat struct {
	//Bgt_wegdeel    string
	min int
	max int
	std int
	avg int
}

type WegDeelScans struct {
	Parkeervak_ids map[string]bool
	scanCount      int
}

type WegDeelHours struct {
	Wegdelen  map[string]*WegDeelScans
	scanCount int
}

func (w *WegDeelScans) Add(pvkey string) {
	w.Parkeervak_ids[pvkey] = true
}

func (m *MonsterMap) setDefault(key string) *WegDeelHours {

	if v, ok := m.Hours[key]; ok {
		return v
	} else {
		val := &WegDeelHours{
			Wegdelen:  make(map[string]*WegDeelScans),
			scanCount: 0,
		}
		m.Hours[key] = val
		return val
	}
}

func (w *WegDeelHours) setDefault(wd string) *WegDeelScans {

	if v, ok := w.Wegdelen[wd]; ok {
		return v
	} else {
		val := &WegDeelScans{
			Parkeervak_ids: make(map[string]bool),
			scanCount:      0,
		}
		w.Wegdelen[wd] = val
		return val
	}
}

type MonsterMap struct {
	Hours map[string]*WegDeelHours
}

func init() {
	// run settings
	SETTINGS.SetInt("workers", 1, "Specify mount of workers")
	SETTINGS.SetInt("monthsago", 1, "start from minus month x from now")

	// postgres settings
	SETTINGS.Set("dbhost", "database", "Specify Elastic search Host")
	SETTINGS.Set("dbpwsd", "insecure", "Set Database Password")
	SETTINGS.Set("dbname", "predictiveparking", "Set database name")
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

	monsterMap = MonsterMap{
		Hours: make(map[string]*WegDeelHours),
		//Wegdelen: make(map[string]*WegDeelScans),
	}
}

func main() {
	//var err error

	// start workers
	chItems := make(chan *Item, 100000)
	workers := SETTINGS.GetInt("workers")

	go printStatus(chItems)

	wg.Add(workers)

	for i := 0; i < workers; i++ {
		go worker(i, chItems)
	}

	fillFromDB(chItems)
	close(chItems)
	wg.Wait()
}

func mapKey(item *Item) string {
	layout := "2006-01-02T15:04:05Z"
	t, err := time.Parse(layout, strings.Replace(item.Scan_moment, `"`, "", 2))
	if err != nil {
		panic(err)
	}
	keylayout := "2006-01-02T15"
	return t.Format(keylayout)
}

func worker(workId int, chItems chan *Item) {

	for item := range chItems {

		mapRows++
		timekey := mapKey(item)

		hourmap := monsterMap.setDefault(timekey)
		wegdeel := hourmap.setDefault(item.Bgt_wegdeel)

		//pvmap.
		wegdeel.Add(item.Parkeervak_id)

	}
	wg.Done()
}

func printStatus(chItems chan *Item) {
	i := 1
	delta := 5
	duration := 0
	speed := 0

	for {
		time.Sleep(time.Duration(delta) * time.Second)

		log.Printf("STATUS: rows:%-10d  %-10d rows/sec  buffer: %d", mapRows, speed, len(chItems))
		duration = i * delta
		speed = mapRows / duration
		i++
	}
}
