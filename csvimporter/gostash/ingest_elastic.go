package main

import (
	"io/ioutil"
	"fmt"
	"log"
	"golang.org/x/net/context"
	"gopkg.in/olivere/elastic.v6"
	"sync"
	"encoding/json"
)


// globals
var client *elastic.Client
var wg sync.WaitGroup

func init() {
	// run settings
	SETTINGS.SetInt("workers", 3, "amount of workers")

	// postgres settings
	SETTINGS.Set("dbhost", "localhost", "amount of workers")
	SETTINGS.Set("dbpwsd", "insecure", "Set Database Password")
	SETTINGS.Set("dbname", "database", "Set database name")
	SETTINGS.Set("dbuser", "user", "Set database user")
	SETTINGS.SetInt("dbport", 5432, "Port under which database runs ")

	// elastic search settings
	SETTINGS.Set("file", "mappings.json", "path to file with elastic search mapping")
	SETTINGS.Set("index", "", "Name of the Elastic Search Index")
	SETTINGS.Set("eshost", "localhost", "Elastic search Hostname ")
	SETTINGS.SetInt("esport", 9200, "Port under which elastic search runs")

	SETTINGS.Parse()
}


func main() {
	var err error
	client, err = elastic.NewClient()
	if err != nil {
		log.Fatal(err)
	}
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
	wg.Add(workers)
	for i:=0; i < workers;i++ {
		go worker(i, chItems, SETTINGS.Get("index"))
	}
	fillFromDB(chItems)
	close(chItems)
	wg.Wait()

}

func worker(workId int, chItems chan *Item, esIndex string) {
	ctx := context.Background()
	for item := range chItems {
		//_, err := client.Index().Index(esIndex).Type("info").Id(strconv.Itoa(item.UserID)).BodyJson(item).Do(ctx)
		itemJson, _ := json.Marshal(&item)
		_, err := client.Index().Index(esIndex).Id(string(item.id)).BodyJson(itemJson).Do(ctx)
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
		log.Fatal(err)
	}
	if !createIndex.Acknowledged {
		fmt.Println("Index not acknowledged, Could be ok?!? or not...")
	}
}
