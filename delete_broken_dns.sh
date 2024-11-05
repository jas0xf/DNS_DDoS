#!/bin/bash

TARGET_FILE="./TW_DNS"
INPUT_FILE="./input"
TEMP_FILE="temp"
MAX_THREADS=10  # Maximum number of concurrent threads

> "$TEMP_FILE"  # Clear the contents of the TEMP_FILE

# Function to check an IP and write to TEMP_FILE if it succeeds
check_ip() {
    local IP="$1"
    if timeout 10 dig google.com @"$IP" | grep "status: NOERROR" > /dev/null 2>&1; then
        echo "$IP" >> "$TEMP_FILE"
        echo "$IP succeeded."
    else
        echo "$IP removed."
    fi
}

# Counter for managing threads
count=0

# Read IPs from the file
while IFS= read -r IP; do
    # Call check_ip in the background
    check_ip "$IP" &
    
    ((count++))

    # If max threads are reached, wait for them to finish
    if (( count >= MAX_THREADS )); then
        wait
        count=0
    fi
done < "$INPUT_FILE"


cp "$TARGET_FILE" "${TARGET_FILE}.bak"
mv "$TEMP_FILE" "$TARGET_FILE"


merge_file() {
    cp "$TARGET_FILE" "${TARGET_FILE}.bak"

  while IFS= read -r IP; do
      if ! grep -q "^$IP$" "$TARGET_FILE"; then
          echo "$IP" >> "$TARGET_FILE"
      fi
  done < "$TEMP_FILE"

  sort -u "$TARGET_FILE" -o "$TARGET_FILE"
  rm "$TEMP_FILE"
}

# merge_file
