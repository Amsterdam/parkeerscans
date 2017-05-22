/*
Index scandata using golang instead of logstash

WIP

*/
package main

import (
	//"encoding/json"
	//"errors"

	"database/sql"
	"fmt"
	_ "github.com/lib/pq"
	"golang.org/x/net/context"
	"sync"

	"log"
	"time"

	elastic "gopkg.in/olivere/elastic.v5"
)

type momentScan struct {
	scan  Scan
	index string
}

//Scan a single licence plate scan
type Scan struct {
	ID                string           `json:"document_id"`
	ScanMoment        time.Time        `json:"@timestamp"`
	ScanID            int              `json:"scan_id"`
	ScanSource        string           `json:"scan_source, omitempty"`
	DeviceID          string           `json:"device_id, omitempty"`
	Sperscode         string           `json:"sperscode, omitempty"`
	Qualcode          string           `json:"qualcode, omitempty"`
	FFDF              string           `json:"ff_df, omitempty"`
	NHAHoogte         float64          `json:"naheffing_hoogte, omitempty"`
	BGTwegdeel        string           `json:"bgt_wegdeel"`
	BGTwegdeelFunctie string           `json:"bgt_wegdeel_functie"`
	Buurtcode         string           `json:"buurtcode"`
	Buurtcombinatie   string           `json:"buurtcombinatie"`
	Stadsdeel         string           `json:"stadsdeel"`
	ParkeervakID      string           `json:"parkeervak_id, omitempty"`
	ParkeervakSoort   string           `json:"parkeervak_soort, omitempty"`
	Geo               elastic.GeoPoint `json:"geo"`

	//round(ST_Y(geometrie)::numeric,8) as lat,
	//round(ST_X(geometrie)::numeric,8) as lon,

	Minute    int `json:"minute"`
	Second    int `json:"minute"`
	Hour      int `json:"hour"`
	Year      int `json:"year"`
	DayOfYear int `json:"day_of_year"`

	Month string `json:"month"`
	Day   string `json:"day"`
}

var (
	ctx context.Context

	//Db object we use all over the place
	Db     *sql.DB
	client elastic.Client
	wg     sync.WaitGroup
)

func init() {

	db, err := dbConnect(ConnectStr())
	Db = db

	panicOnErr(err)

	//batch := 5000

}

func main() {

	ctx := context.Background()

	fmt.Println("Importing scandata into elastic")

	client, err := elastic.NewSimpleClient(
		elastic.SetURL("http://elasticsearch:9200"),
		elastic.SetSniff(false),
	)
	panicOnErr(err)

	// Ping the Elasticsearch server to get e.g. the version number
	info, code, err := client.Ping("http://elasticsearch:9200").Do(ctx)
	if err != nil {
		// Handle error
		panic(err)
	}
	fmt.Printf("\n Elasticsearch returned with code %d and version %s \n", code, info.Version.Number)

	jsonscans := make(chan momentScan, 5000)

	wg.Add(1)
	go fetchScans(jsonscans)
	wg.Add(1)
	go indexScans(jsonscans)

	wg.Wait()

}

//PanicOnErr default crash hard error handling
func panicOnErr(err error) {
	if err != nil {
		panic(err)
	}
}

//timeTrack
func timeTrack(start time.Time, name string) {
	elapsed := time.Since(start)
	log.Printf("%s took %s", name, elapsed)
}
