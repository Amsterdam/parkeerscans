package main

import (
	"testing"
)

func TestCleanFilename(t *testing.T) {
	testcases := []struct {
		got  string
		want string
	}{
		// Happy path
		{"name", "name"},
		{"name.txt", "name.txt"},

		// filter multiple dots in in succesion
		{"............txt", ".txt"},
		{"n.n.n.n.txt", "n.n.n.n.txt"},
		{"...........name.......txt", ".name.txt"},

		// Remove characters that are outside of alphabet
		{"日本語", ""},
		{"!@#$%^&*()_+`", ""},
		{"	,\n\r, \n?<>\"", ""},
		{"1234567890", ""},
		{"ä本\t\000\007\377\x07\xff\u12e4\U00101234", ""},

		// Use string literal
		{`日本語`, ""},
		{`!@#$%^&*()_+\`, ""},
		{`	,\n\r, \n?<>\"`, "nrn"},
		{`ä本\t\000\007\377\x07\xff\u12e4\U00101234`, "txxffueU"},

		// Some common path travesals
		{"../name.txt", ".name.txt"},
		{"..\name.txt", ".ame.txt"},
		{"..././name.txt", ".name.txt"},
		{"...\\.\name.txt", ".ame.txt"},
		{"%2e%2e%2f.name.txt", "eef.name.txt"},
		{"%uff0e%uff0e%u2215name.txt", "uffeuffeuname.txt"},
		{".%uff0e%uff0e%u2215name.txt", ".uffeuffeuname.txt"},
		{"%c0%ae%c0%ae%c0%afname.txt", "caecaecafname.txt"},
		{"\000\000name.txt", "name.txt"},
		{"\x00\x00\x00name.txt", "name.txt"},
		{"\\z\\zname.txt", "zzname.txt"},
		{"\u0000\u0000name.txt", "name.txt"},
	}

	for testcaseNumber, testcase := range testcases {
		result := cleanFilename(testcase.got)
		if result != testcase.want {
			t.Error("testcase: ", testcaseNumber+1, "result:", result, "!=", testcase.want)
		}
	}
}
