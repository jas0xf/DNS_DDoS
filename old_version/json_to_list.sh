#!/bin/bash

JSON_FILE="TW_DNS.json"
OUTPUT_FILE="input"

# Extract the "ip" field from each line and save it to the output file
jq -r '.ip' "$JSON_FILE" > "$OUTPUT_FILE"
