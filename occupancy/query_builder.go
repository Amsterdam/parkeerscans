package main

import (
	"fmt"
)

// This function is not safe to use for user specified input
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
		return fmt.Sprintf("%s WHERE %s AND %s LIMIT 100000;", baseQuery, startQ, endQ)
	case hasStart:
		return fmt.Sprintf("%s WHERE %s LIMIT 100000;", baseQuery, startQ)
	case hasEnd:
		return fmt.Sprintf("%s WHERE %s LIMIT 100000;", baseQuery, endQ)
	default:
		return baseQuery + "LIMIT 100000;"
	}
}
