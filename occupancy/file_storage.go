package main

import (
	"bufio"
	"encoding/json"
	"log"
	"os"
)

func storeTofile(items Scans) {
	filename := cleanFilename(SETTINGS.Get("storefile"))
	file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	for _, item := range items {
		itemJSON, _ := json.Marshal(&item)
		if _, err = file.WriteString(string(itemJSON) + "\n"); err != nil {
			panic(err)
		}
	}
}

func loadFile() {
	filename := cleanFilename(SETTINGS.Get("storefile"))
	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	count := 0
	for scanner.Scan() {
		count++
		if err := scanner.Err(); err != nil {
			log.Fatal(err)
		}
		var row Scan
		err := json.Unmarshal([]byte(scanner.Text()), &row)
		if err != nil {
			log.Fatal(err)
		}
		AllScans = append(AllScans, &row)
	}
}

// whitelist string only allow alphabet characters lower and upper case.
// And allows for one "." in succesion.
func cleanFilename(s string) string {
	rr := []rune(s)
	n := []rune{}
	f := false
	for _, r := range rr {
		if r >= 'A' && r <= 'Z' {
			f = false
			n = append(n, r)
		}
		if r >= 'a' && r <= 'z' {
			f = false
			n = append(n, r)
		}
		if r == 46 && !f {
			f = true
			n = append(n, r)
		}
	}
	return string(n)
}
