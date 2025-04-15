#!/bin/bash

# Input and Output CSV file names
input_csv="input.csv"
output_csv="output.csv"

# Initialize the output CSV file with headers
echo "VirtualServerName;iRules" > "$output_csv"

# Read the CSV file line by line (skip the header)
tail -n +2 "$input_csv" | while IFS=, read virtual_server
do
    # Query the virtual server using tmsh
    tmsh_output=$(tmsh list ltm virtual "$virtual_server")

    # Extract the iRules from the rules block using sed and cleaning up the output
    irules=$(echo "$tmsh_output" | sed -n '/rules {/,/}/p' | grep -v 'rules {' | grep -v '}' | xargs | tr ' ' ';')

    # Append the virtual server name and iRules to the output CSV
    echo "$virtual_server;$irules" >> "$output_csv"
done

echo "Processing complete. Output written to $output_csv"
