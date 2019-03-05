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
	"syscall"

	"golang.org/x/net/context"
	"gopkg.in/olivere/elastic.v6"
)

// globals
var client *elastic.Client
var wg sync.WaitGroup
var elkRows int

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
	SETTINGS.Set("index", "scan", "Name of the Elastic Search Index")
	SETTINGS.Set("eshost", "elasticsearch", "Elastic search Hostname ")
	SETTINGS.SetInt("esport", 9200, "Port under which elastic search runs")
	SETTINGS.SetInt("esbuffer", 100, "Buffer items before sending to elasticsearch")

	SETTINGS.Parse()
	elkRows = 0
}

func main() {
	var err error
	client, err = elastic.NewClient(
		elastic.SetURL(fmt.Sprintf("http://%s:%d", SETTINGS.Get("eshost"), SETTINGS.GetInt("esport"))),
		elastic.SetRetrier(NewCustomRetrier()),
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

	// set Mapping to index
	setIndex(SETTINGS.Get("index"), mapping)

	// start workers
	chItems := make(chan *Item, 1000)
	workers := SETTINGS.GetInt("workers")

	go printStatus(chItems)

	wg.Add(workers)
	for i := 0; i < workers; i++ {
		go worker(i, chItems, SETTINGS.Get("index"), SETTINGS.GetInt("esbuffer"))
	}
	fillFromDB(chItems)
	close(chItems)
	wg.Wait()

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

func worker(workId int, chItems chan *Item, esIndex string, esbuffer int) {
	ctx := context.Background()
	bulkData := client.Bulk()
	buffer := 0
	for item := range chItems {
		elkRows += 1
		itemJson, err := json.Marshal(item)

		if err != nil {
			log.Fatal("marschall", string(itemJson))
		}

		rec := elastic.NewBulkIndexRequest().Index(esIndex).Type("scan").Id(string(item.Id)).Doc(string(itemJson))
		buffer++
		bulkData = bulkData.Add(rec)
		if buffer >= 1000 {
			_, err := bulkData.Do(ctx)
			buffer = 0
			if err != nil {
				log.Println("ow no", err)
				log.Println("ow no", string(itemJson))
			}
		}
	}
	if buffer > 0 {
		fmt.Println("Adding last items", buffer)
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
		fmt.Println("If index is already set, Ingore the following error message.\n", err)
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
