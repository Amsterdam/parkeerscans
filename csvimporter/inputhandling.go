package main

import (
	"os"
	"strconv"
)

// Handle input from environment or flags
// Order of preference:
// 1. Commmand line argument
// 2. Environment variable
// 3. Default given
func handleInputString(varStr, defaultStr, key string) string {
	if len(varStr) > 0 {
		return varStr
	}
	varEnv, found := os.LookupEnv(key)
	if found {
		return varEnv
	}
	return defaultStr
}

// Handle input from environment or flags
// Order of preference:
// 1. Commmand line argument
// 2. Environment variable
// 3. Default given
func handleInputInt(varInt, defaultInt int, key string) int {
	if varInt != -1 {
		return varInt
	}
	varEnv, found := os.LookupEnv(key)
	if found {
		if n, err := strconv.Atoi(varEnv); err == nil {
			return n
		}
	}
	return defaultInt
}
