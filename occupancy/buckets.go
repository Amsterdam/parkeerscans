package main

import (
	"fmt"
	"math"
)

type vakIDMap struct {
	uniqevakken map[string]bool
}

type wegdeelAggregator struct {
	bucket        map[string]*vakIDMap
	scanCount     int64
	fiscaleVakken int64
	vakken        int64
}

func (wda *wegdeelAggregator) stats() (int64, int64, int64, int64, int64) {
	min := int64(100)
	max := int64(0)
	sum := int64(0)

	std := int64(0)
	avg := int64(0)

	occupancies := []int64{}
	stddelta := []int64{}
	stdsum := int64(0)

	bucketCount := int64(len(wda.bucket))

	for _, bucket := range wda.bucket {
		occupancy := int64(
			float64(len(bucket.uniqevakken)) / float64(wda.vakken) * 100)
		occupancies = append(occupancies, occupancy)

		if occupancy < min {
			min = occupancy
		}

		if occupancy > max {
			//make sure we do not go over 100%.
			//which is possible when parking spots are
			//removed.
			if occupancy > 100 {
				occupancy = 100
			}
			max = occupancy
		}

		sum = sum + occupancy

	}

	avg = int64(sum / bucketCount)

	for v := range occupancies {
		delta := int(v) - int(avg)
		delta = int(math.Abs(float64(delta)))
		stddelta = append(stddelta, int64(delta))
		stdsum += int64(delta)
	}

	std = int64(math.Sqrt(float64(int(stdsum) / len(stddelta))))

	return bucketCount, min, max, std, avg

}

func (vkh *vakIDMap) addpvID(pvID string) {

	if vkh.uniqevakken == nil {
		vkh.uniqevakken = make(map[string]bool)
	}

	vkh.uniqevakken[pvID] = true
}

func (wa *wegdeelAggregator) addHourKey(hourkey string, pvID string) {
	if _, ok := wa.bucket[hourkey]; !ok {
		wa.bucket[hourkey] = &vakIDMap{
			uniqevakken: make(map[string]bool),
		}
	}
	wa.scanCount++
	wa.bucket[hourkey].addpvID(pvID)
}

type buckets struct {
	wegdelen map[string]*wegdeelAggregator
}

func (e *buckets) addWegdeel(wd string, hourkey string, pvID string) {

	if e.wegdelen == nil {
		e.wegdelen = make(map[string]*wegdeelAggregator)
	}

	if _, ok := e.wegdelen[wd]; !ok {
		e.wegdelen[wd] = &wegdeelAggregator{
			bucket:        make(map[string]*vakIDMap),
			fiscaleVakken: wegdelen[wd].fiscaleVakken,
			vakken:        wegdelen[wd].vakken,
		}
	}

	e.wegdelen[wd].addHourKey(hourkey, pvID)
}

func fillWegDeelVakkenByBucket(filteredScans Scans) wegdeelResponse {

	//var wdID string
	bucketResult := buckets{}

	for _, scan := range filteredScans {
		wdID := scan.bgtWegdeel
		hourkey := scan.getMapHourID()
		pvID := scan.ParkeervakID

		if _, ok := wegdelen[wdID]; !ok {
			continue
		}
		bucketResult.addWegdeel(wdID, hourkey, pvID)
	}

	fmt.Println(len(bucketResult.wegdelen))
	aEndResult := wegdeelResponse{}

	for wdID, wdAgg := range bucketResult.wegdelen {

		wdSource := wegdelen[wdID]

		if wdSource == nil {
			continue
		}

		bcount, min, max, std, avg := wdAgg.stats()

		wdOccupancy := &wegdeelOccupancyResult{
			ID:    wdSource.ID,
			BgtID: wdSource.bgtID,
			//bgtFunctie:    wdSource.bgtFunctie,
			Geometrie:     wdSource.geometrie,
			Vakken:        wdSource.vakken,
			FiscaleVakken: wdSource.fiscaleVakken,
			Buurt:         wdSource.buurt,
			ScanCount:     wdAgg.scanCount,
			BuckerCount:   bcount,
			AvgOccupany:   avg,
			MinOccupany:   min,
			MaxOccupany:   max,
			StdOccupany:   std,
		}
		aEndResult = append(aEndResult, wdOccupancy)
	}

	return aEndResult
}
