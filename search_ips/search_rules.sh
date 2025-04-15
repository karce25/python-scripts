#!/bin/bash

# Input and Output CSV file names
input_csv="input.csv"
output_csv="output.csv"

# Temporary file for processing
temp_file="temp_file.csv"

# Initialize the output CSV file with headers
echo "VirtualServerName,iRules" > "$output_csv"

# Read the CSV file line by line (skip the header)
tail -n +2 "$input_csv" | while IFS=, read virtual_server
do
    # Use tmsh to list details of the virtual server
    tmsh_output=$(tmsh list ltm virtual "$virtual_server")

    # Extract the iRules from the output (assuming iRules are listed in the `rules` field)
    irules=$(echo "$tmsh_output" | grep 'rules {' -A 10 | grep -v 'rules {' | grep -v '}' | xargs | tr ' ' ',')

    # Append the virtual server name and iRules to the output CSV
    echo "$virtual_server,$irules" >> "$output_csv"
done

echo "Processing complete. Output written to $output_csv"
