package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"sync"
	"time"

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

	SETTINGS.Parse()
	elkRows = 0
}

func main() {
	var err error
	client, err = elastic.NewClient(
	elastic.SetURL(fmt.Sprintf("http://%s:%d", SETTINGS.Get("eshost"), SETTINGS.GetInt("esport"))),
	//	elastic.SetMaxRetries(5),
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
		go worker(i, chItems, SETTINGS.Get("index"))
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

func worker(workId int, chItems chan *Item, esIndex string) {
	ctx := context.Background()
	for item := range chItems {
		elkRows += 1
		//_, err := client.Index().Index(esIndex).Type("info").Id(strconv.Itoa(item.UserID)).BodyJson(item).Do(ctx)
		itemJson, err := json.Marshal(item)

		if err != nil {
			log.Fatal("marschall", string(itemJson))
		}

		_, err =
			client.Index().Index(esIndex).
				Type("scan").Id(string(item.Id)).
				BodyJson(string(itemJson)).Do(ctx)

		if err != nil {
			log.Println("ow no", err)
			log.Println("ow no", string(itemJson))
		}
	}
	wg.Done()
}

func setIndex(index, mapping string) {
	ctx := context.Background()
	createIndex, err := client.CreateIndex(index).BodyString(mapping).Do(ctx)
	if err != nil {
		fmt.Println(err)
		return
	}
	if !createIndex.Acknowledged {
		fmt.Println("Index not acknowledged, Could be ok?!? or not...")
	}
}
