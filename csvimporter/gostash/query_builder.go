package main

import (
	"fmt"
)

func queryDateBuilder(baseQuery, column, start, end string) string {
	if baseQuery[len(baseQuery)-1] == ';' {
		baseQuery = baseQuery[:len(baseQuery)-1]
	}
	startQ := fmt.Sprintf("%s >= '%s'", column, start)
	endQ := fmt.Sprintf("%s < '%s'", column, end)

	hasStart := start != ""
	hasEnd := end != ""
	switch {
	case hasStart && hasEnd:
		return fmt.Sprintf("%s WHERE %s AND %s;", baseQuery, startQ, endQ)
	case hasStart:
		return fmt.Sprintf("%s WHERE %s;", baseQuery, startQ)
	case hasEnd:
		return fmt.Sprintf("%s WHERE %s;", baseQuery, endQ)
	default:
		return baseQuery + ";"
	}
}
