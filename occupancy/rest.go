package main

import (
	"encoding/json"
	"net/http"
	"strconv"
)

//ErrorMsg Response structs
type ErrorMsg struct {
	Error      string
	Reason     string
	HTTPStatus int
}

func filterEmpty(ss []string) []string {
	newS := []string{}
	for _, item := range ss {
		if len(item) >= 1 {
			newS = append(newS, item)
		}
	}
	return newS
}

func ErrorResponse(w http.ResponseWriter, reason string, httpStatus int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(httpStatus)
	json.NewEncoder(w).Encode(ErrorMsg{Error: "Error", Reason: reason, HTTPStatus: httpStatus})
}

func rest(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	//search := filterEmpty(strings.Split(r.URL.Path, "/"))

	item := AllScans
	json.NewEncoder(w).Encode(item)
	return

	var items Scans

	w.Header().Set("Total-Items", strconv.Itoa(len(items)))
	w.WriteHeader(http.StatusOK)

	json.NewEncoder(w).Encode(items)
}

var registerFuncs = make(map[string]filterFunc)
