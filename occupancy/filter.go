package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"time"

	"runtime"
	//	"runtime/debug"
	//	"github.com/pkg/profile"
)

type filterFuncc func(*Scan, string) bool
type registerFuncType map[string]filterFuncc
type registerGroupByFunc map[string]func(*Scan) string
type filterType map[string][]string

type formatRespFunc func(w http.ResponseWriter, r *http.Request, wd wegdeelResponse)
type registerFormatMap map[string]formatRespFunc

// Filter Functions
func filterStadsdeelContains(i *Scan, s string) bool {
	return strings.Contains(i.Stadsdeel, s)
}

func filterBuurtoceContains(i *Scan, s string) bool {
	return strings.Contains(i.Buurtcode, s)
}

func filterWeekdayContains(i *Scan, s string) bool {
	weekday := i.ScanMoment.Weekday().String()
	weekday = strings.ToLower(weekday)
	return weekday == s
}

func filterHourContains(i *Scan, s string) bool {
	hour := i.ScanMoment.Hour()
	input, err := strconv.Atoi(s)
	if err != nil {
		fmt.Println("invalid hour input")
		return false
	}
	return hour == input
}

func filterIsWeekend(i *Scan, s string) bool {
	isWeekend := i.ScanMoment.Weekday() >= 5
	return isWeekend
}

func filterBeforeDate(i *Scan, s string) bool {
	filterTime, err := time.Parse("2006-01-02", s)
	if err != nil {
		return false
	}
	if i == nil {
		fmt.Println("i == nil")
		return false
	}
	return i.ScanMoment.Before(filterTime)
}

func filterAfterDate(i *Scan, s string) bool {
	filterTime, err := time.Parse("2006-01-02", s)
	if err != nil {
		return false
	}
	return i.ScanMoment.After(filterTime)
}

func filterMatchDate(i *Scan, s string) bool {
	filterTime, err := time.Parse("2006-01-02", s)
	if err != nil {
		return false
	}
	y1, m1, d1 := i.ScanMoment.Date()
	y2, m2, d2 := filterTime.Date()
	return y1 == y2 && m1 == m2 && d1 == d2
}

//Runner of filter functions, Scan Should pass all
func all(item *Scan, filters filterType, registerFuncs registerFuncType) bool {
	for funcName, args := range filters {
		filterFunc := registerFuncs[funcName]
		if filterFunc == nil {
			continue
		}
		for _, arg := range args {
			if !filterFunc(item, arg) {
				return false
			}
		}
	}
	return true
}

//Runner of exlude functions, Scan Should pass all
func exclude(item *Scan, excludes filterType, registerFuncs registerFuncType) bool {
	for funcName, args := range excludes {
		excludeFunc := registerFuncs[funcName]
		if excludeFunc == nil {
			continue
		}
		for _, arg := range args {
			if excludeFunc(item, arg) {
				return false
			}
		}
	}
	return true
}

func filtered(items Scans, filters filterType, excludes filterType, registerFuncs registerFuncType) Scans {
	filteredScans := Scans{}
	for _, item := range items {
		if !all(item, filters, registerFuncs) {
			continue
		}
		if !exclude(item, excludes, registerFuncs) {
			continue
		}
		filteredScans = append(filteredScans, item)
	}
	return filteredScans
}

func mapIndex(scans Scans, indexes []int) Scans {
	o := Scans{}
	for _, index := range indexes {
		o = append(o, scans[index])
	}
	return o
}

var registerFuncMap registerFuncType
var registerGroupBy registerGroupByFunc
var registerFormat registerFormatMap

func init() {
	registerFuncMap = make(registerFuncType)
	registerFuncMap["stadsdeel"] = filterStadsdeelContains
	registerFuncMap["buurtcode"] = filterBuurtoceContains
	registerFuncMap["weekday"] = filterWeekdayContains
	registerFuncMap["hour"] = filterHourContains
	registerFuncMap["isweekend"] = filterIsWeekend
	registerFuncMap["before"] = filterBeforeDate
	registerFuncMap["after"] = filterAfterDate
	registerFuncMap["match"] = filterMatchDate

	registerGroupBy = make(registerGroupByFunc)
	registerGroupBy["day"] = groupByDay
	registerGroupBy["weekend"] = groupByWeekend
	registerGroupBy["year"] = groupByYear

	registerFormat = make(registerFormatMap)
	registerFormat["json"] = formatResponseJSON
	registerFormat["csv"] = formatResponseCSV
}

// API

func listRest(w http.ResponseWriter, r *http.Request) {
	filterMap, excludeMap := parseURLParameters(r)

	filterScans := filtered(AllScans, filterMap, excludeMap, registerFuncMap)

	//w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Total-Items", strconv.Itoa(len(filterScans)))
	//w.WriteHeader(http.StatusOK)

	//groupByS, groupByFound := r.URL.Query()["groupby"]
	//if !groupByFound {
	//	json.NewEncoder(w).Encode(filterScans)
	//	return
	//}

	// this should go rest service.
	aEndResult := fillWegDeelVakkenByBucket(filterScans)
	//responseJSON, _ := json.Marshal(aEndResult)
	// groupByItems := groupByRunner(items, groupByS[0])
	// json.NewEncoder(w).Encode(aEndResult)
	FormatAndSend(w, r, aEndResult)
	//garbage collection
	go func() {
		time.Sleep(2 * time.Second)
		runtime.GC()
	}()
}

func helpRest(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	response := make(map[string][]string)
	registeredFilters := []string{}
	for k := range registerFuncMap {
		registeredFilters = append(registeredFilters, k)
	}
	registeredGroupbys := []string{}
	for k := range registerGroupBy {
		registeredGroupbys = append(registeredGroupbys, k)
	}
	response["filters"] = registeredFilters
	response["groupby"] = registeredGroupbys
	w.WriteHeader(http.StatusOK)

	json.NewEncoder(w).Encode(response)
}

// util for api
func parseURLParameters(r *http.Request) (filterType, filterType) {
	filterMap := make(filterType)
	excludeMap := make(filterType)
	for k := range registerFuncMap {
		parameter, parameterFound := r.URL.Query()[k]
		if parameterFound {
			filterMap[k] = parameter
		}
		parameter, parameterFound = r.URL.Query()["!"+k]
		if parameterFound {
			excludeMap[k] = parameter
		}
	}
	return filterMap, excludeMap
}

// Group by functions

func groupByYear(i *Scan) string {
	return strconv.Itoa(int(i.ScanMoment.Year()))
}

func groupByWeekend(i *Scan) string {
	isWeekend := i.ScanMoment.Weekday() >= 5
	if isWeekend {
		return "weekend"
	}
	return "weekday"
}

func groupByDay(i *Scan) string {
	return strings.ToLower(i.ScanMoment.Weekday().String())
}

func groupByRunner(items Scans, groubByParameter string) ScansGroupedBy {
	grouping := make(ScansGroupedBy)
	groupingFunc := registerGroupBy[groubByParameter]
	if groupingFunc == nil {
		return grouping
	}
	for _, item := range items {
		GroupingKey := groupingFunc(item)
		grouping[GroupingKey] = append(grouping[GroupingKey], item)
	}
	return grouping
}

func printMemUsage() {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	// For info on each, see: https://golang.org/pkg/runtime/#MemStats
	fmt.Printf("Alloc = %v MiB", bToMb(m.Alloc))
	fmt.Printf("\tTotalAlloc = %v MiB", bToMb(m.TotalAlloc))
	fmt.Printf("\tSys = %v MiB", bToMb(m.Sys))
	fmt.Printf("\tNumGC = %v\n", m.NumGC)
}

func bToMb(b uint64) uint64 {
	return b / 1024 / 1024
}

func runPrintMem() {
	for {
		printMemUsage()
		time.Sleep(4 * time.Second)
	}
}

func formatResponseJSON(w http.ResponseWriter, r *http.Request, items wegdeelResponse) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(items)
}

func formatResponseCSV(w http.ResponseWriter, r *http.Request, items wegdeelResponse) {
	w.Header().Set("Content-Type", "text/csv")
	w.Header().Set("Content-Disposition", "attachment;filename=output.csv")
	wr := csv.NewWriter(w)
	if err := wr.Write(items[0].Columns()); err != nil {
		log.Fatal(err)
	}
	for _, item := range items { // make a loop for 100 rows just for testing purposes
		if err := wr.Write(item.Row()); err != nil {
			log.Fatal(err)
		}
	}
	wr.Flush() // writes the csv writer data to  the buffered data io writer(b(bytes.buffer))
}

func FormatAndSend(w http.ResponseWriter, r *http.Request, items wegdeelResponse) {
	respFormatSlice, respFormatFound := r.URL.Query()["format"]
	respFormat := ""
	if respFormatFound {
		respFormat = respFormatSlice[0]
	}

	w.Header().Set("Total-Items", strconv.Itoa(len(items)))
	w.WriteHeader(http.StatusOK)

	respFormatFunc, found := registerFormat[respFormat]
	if !found {
		respFormatFunc = registerFormat["json"]
	}
	respFormatFunc(w, r, items)
}
