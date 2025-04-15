#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -i <input_csv> -o <output_csv>"
    exit 1
}

# Parse arguments
while getopts "i:o:" opt; do
    case $opt in
        i)
            input_csv=$OPTARG
            ;;
        o)
            output_csv=$OPTARG
            ;;
        *)
            usage
            ;;
    esac
done

# Check if both input and output arguments are provided
if [[ -z $input_csv || -z $output_csv ]]; then
    usage
fi

# Initialize the output CSV file with headers
echo "VirtualServerName,iRules,SNAT" > "$output_csv"

# Read the CSV file line by line (skip the header)
tail -n +2 "$input_csv" | while IFS=, read virtual_server
do
    # Query the virtual server using tmsh
    tmsh_output=$(tmsh list ltm virtual "$virtual_server")

    # Extract the iRules and separate them with semicolons
    irules=$(echo "$tmsh_output" | sed -n '/rules {/,/}/p' | grep -v 'rules {' | grep -v '}' | xargs | tr ' ' ';')

    # Extract the SNAT value (if present)
    # Look for the "source-address-translation" block and retrieve the type (e.g., "automap") or any custom value
    snat=$(echo "$tmsh_output" | sed -n '/source-address-translation {/,/}/p' | grep 'type' | awk '{print $2}')
    if [[ -z $snat ]]; then
        snat="None"  # Use "None" if SNAT is not present
    fi

    # Append the virtual server name, iRules, and SNAT value to the output CSV, using commas for column separation
    echo "$virtual_server,\"$irules\",$snat" >> "$output_csv"
done

echo "Processing complete. Output written to $output_csv"
