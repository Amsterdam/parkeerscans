package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"sync"
	"time"

	// elastic retries
	"errors"
	"net/http"
	"strings"
	"syscall"

	"golang.org/x/net/context"
	"gopkg.in/olivere/elastic.v6"
)

// globals
var client *elastic.Client
var wg sync.WaitGroup
var elkRows int
var syncIndex *syncIndexes

func init() {
	// run settings
	SETTINGS.SetInt("workers", 30, "amount of workers")

	// postgres settings
	SETTINGS.Set("dbhost", "database", "amount of workers")
	SETTINGS.Set("dbpwsd", "insecure", "Set Database Password")
	SETTINGS.Set("dbname", "predictiveparking", "Set database name")
	SETTINGS.Set("dbuser", "user", "Set database user")
	SETTINGS.SetInt("dbport", 5432, "Port under which database runs ")

	// elastic search settings
	SETTINGS.Set("file", "mappings.json", "path to file with elastic search mapping")
	SETTINGS.Set("index", "not-set", "Name of the Elastic Search Index")
	SETTINGS.Set("eshost", "elasticsearch", "Elastic search Hostname ")
	SETTINGS.SetInt("esport", 9200, "Port under which elastic search runs")
	SETTINGS.SetInt("esbuffer", 100, "Buffer items before sending to elasticsearch")

	SETTINGS.Parse()
	elkRows = 0
	syncIndex = &syncIndexes{
		Indexes: make(map[string]bool),
	}
}

func main() {
	var err error
	client, err = elastic.NewClient(
		elastic.SetURL(fmt.Sprintf("http://%s:%d", SETTINGS.Get("eshost"), SETTINGS.GetInt("esport"))),
		elastic.SetRetrier(NewCustomRetrier()),
		elastic.SetSniff(false),
	)
	if err != nil {
		log.Fatal(err)
	}
	defer client.Stop()
	// get mapping json file as string
	mappingBuff, err := ioutil.ReadFile(SETTINGS.Get("file"))
	if err != nil {
		log.Fatal(err)
	}

	mapping := string(mappingBuff)
	syncIndex.DefaultMapping = mapping

	// set Mapping to index
	if SETTINGS.Get("index") != "not-set" {
		setIndex(SETTINGS.Get("index"), mapping)
	}

	// start workers
	chItems := make(chan *Item, 100000)
	workers := SETTINGS.GetInt("workers")

	go printStatus(chItems)

	wg.Add(workers)
	for i := 0; i < workers; i++ {
		go worker(i, chItems, SETTINGS.Get("index"), SETTINGS.GetInt("esbuffer"))
	}
	fillFromDB(chItems)
	close(chItems)
	wg.Wait()

	// Check total items in elastic
	//time.Sleep(10 * time.Second)
	checkTotalItemsAdded()
}

func worker(workId int, chItems chan *Item, esIndex string, esbuffer int) {
	ctx := context.Background()
	bulkData := client.Bulk()
	buffer := 0
	for item := range chItems {
		elkRows += 1
		itemJson, err := json.Marshal(item)

		if err != nil {
			fmt.Println("unable to Json Marshal", string(itemJson))
			fmt.Println(err)
			continue
		}

		// README if index of toplevel is needed comment out the following line
		// IF statement at this level is expensive
		esIndex, err = customEsIndex(item)
		if err != nil {
			fmt.Println("unable to parse scan_moment as date", item.Scan_moment)
			fmt.Println(err)
			continue
		}

		// README if no custom index is set this step is not needed.
		// sync new mapping for index before item is added,
		// If slice of string with new indexes is kept this could be moved to be done before bulk is sent
		syncIndex.Set(esIndex)

		rec := elastic.NewBulkIndexRequest().Index(esIndex).Type("scan").Id(string(item.Id)).Doc(string(itemJson))
		buffer++
		bulkData = bulkData.Add(rec)
		if buffer >= esbuffer {
			_, err := bulkData.Do(ctx)
			buffer = 0
			if err != nil {
				log.Println("ow no", err)
			}
		}
	}
	// sent remaining items to elastic
	if buffer > 0 {
		fmt.Println("Sending last items to elastic. amount:", buffer)
		_, err := bulkData.Do(ctx)
		if err != nil {
			log.Println("ow no", err)
		}
	}
	wg.Done()
}

func setIndex(index, mapping string) {
	ctx := context.Background()
	createIndex, err := client.CreateIndex(index).BodyString(mapping).Do(ctx)
	if err != nil {
		// Remove clutter from output
		//fmt.Println("If index is already set, Ingore the following error message.\n", err)
		return
	}
	if !createIndex.Acknowledged {
		fmt.Println("Index not acknowledged, Could be ok?!? or not...")
	}
}

type CustomRetrier struct {
	backoff elastic.Backoff
}

func NewCustomRetrier() *CustomRetrier {
	return &CustomRetrier{
		backoff: elastic.NewExponentialBackoff(10*time.Millisecond, 8*time.Second),
	}
}

func (r *CustomRetrier) Retry(ctx context.Context, retry int, req *http.Request, resp *http.Response, err error) (time.Duration, bool, error) {
	// Fail hard on a specific error
	if err == syscall.ECONNREFUSED {
		return 0, false, errors.New("Elasticsearch or network down")
	}

	// Stop after 5 retries
	if retry >= 5 {
		return 0, false, nil
	}

	// Let the backoff strategy decide how long to wait and whether to stop
	wait, stop := r.backoff.Next(retry)
	return wait, stop, nil
}

//Global struct for index mapping
//Index that are created should be added only once
//And before the item is stored in elastic search
type syncIndexes struct {
	Indexes        map[string]bool
	DefaultMapping string
	mu             sync.RWMutex
}

func (s *syncIndexes) Set(index string) {
	s.mu.RLock()
	indexFound := s.Indexes[index]
	s.mu.RUnlock()
	if !indexFound {
		s.Update(index)
	}
}

func (s *syncIndexes) Update(index string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	setIndex(index, s.DefaultMapping)
	s.Indexes[index] = true
}

func customEsIndex(item *Item) (string, error) {
	layout := "2006-01-02T15:04:05Z"
	t, err := time.Parse(layout, strings.Replace(item.Scan_moment, `"`, "", 2))
	return fmt.Sprintf("scans-%d.%02d.%02d", t.Year(), t.Month(), t.Day()), err
}

func checkTotalItemsAdded() {
	ctx := context.Background()
	indexes := []string{}
	for key := range syncIndex.Indexes {
		indexes = append(indexes, key)
	}

	count, err := client.Count(indexes...).Do(ctx)
	fmt.Println("indexes Added:", indexes)
	fmt.Println("items found in elastic", count, "rows Added", elkRows,
		"was a successfull:", count > int64(elkRows))
	fmt.Println("err", err)
}

func printStatus(chItems chan *Item) {
	i := 1
	delta := 10
	duration := 0
	speed := 0

	for {
		time.Sleep(time.Duration(delta) * time.Second)

		log.Printf("STATUS: rows:%-10d  %-10d rows/sec  buffer: %d", elkRows, speed, len(chItems))
		duration = i * delta
		speed = elkRows / duration
		i++
	}
}
