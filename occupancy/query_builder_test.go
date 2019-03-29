package main

import (
	"testing"
)

func TestQueryBuilder(t *testing.T) {
	testcases := []struct {
		inputBaseQuery string
		inputColumn    string
		inputStart     string
		inputEnd       string
		expected       string
	}{
		{"SELECT * FROM foo", "bar", "", "", "SELECT * FROM foo;"},
		{"SELECT * FROM foo", "bar", "2018-06-28", "", "SELECT * FROM foo WHERE bar >= '2018-06-28';"},
		{"SELECT * FROM foo", "bar", "", "2018-06-29", "SELECT * FROM foo WHERE bar < '2018-06-29';"},
		{"SELECT * FROM foo", "bar", "2018-06-28", "2018-06-29", "SELECT * FROM foo WHERE bar >= '2018-06-28' AND bar < '2018-06-29';"},

		// Query ends with semicolon
		{"SELECT * FROM foo;", "bar", "", "", "SELECT * FROM foo;"},
		{"SELECT * FROM foo;", "bar", "2018-06-28", "", "SELECT * FROM foo WHERE bar >= '2018-06-28';"},
		{"SELECT * FROM foo;", "bar", "2018-06-28", "2018-06-29", "SELECT * FROM foo WHERE bar >= '2018-06-28' AND bar < '2018-06-29';"},
		{"SELECT * FROM foo;", "bar", "", "2018-06-29", "SELECT * FROM foo WHERE bar < '2018-06-29';"},
	}

	for testcaseNumber, testcase := range testcases {
		result := queryDateBuilder(testcase.inputBaseQuery, testcase.inputColumn, testcase.inputStart, testcase.inputEnd)
		if result != testcase.expected {
			t.Error("testcase: ", testcaseNumber+1, "result:", result, "!=", testcase.expected)
		}
	}
}
