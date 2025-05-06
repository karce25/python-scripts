#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -i input.csv -o output.csv"
    exit 1
}

# Parse command-line arguments
while getopts "i:o:" opt; do
    case "$opt" in
        i) INPUT_CSV="$OPTARG" ;;
        o) OUTPUT_CSV="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if both input and output files are provided
if [[ -z "$INPUT_CSV" || -z "$OUTPUT_CSV" ]]; then
    echo "Error: Missing required arguments."
    usage
fi

# Check if input file exists
if [[ ! -f "$INPUT_CSV" ]]; then
    echo "Error: Input file not found: $INPUT_CSV"
    exit 1
fi

# Add a header to the output CSV
echo "ServerName,RelatedVirtuals,Pools" > "$OUTPUT_CSV"

# Read the input CSV line by line (skip the header)
tail -n +2 "$INPUT_CSV" | while IFS=, read -r server_name; do
    # Extract the base name by removing the suffix (_A, _B, etc.)
    base_name=$(echo "$server_name" | sed -E 's/_[^_]+$//')

    # Use the base name to search in tmsh configuration for related servers
    related_virtuals=$(tmsh list ltm virtual | grep -o "${base_name}_[^ ]*" | grep -v "$server_name" | tr '\n' ';')

    # Initialize a variable for storing pool names
    pools=""

    # Iterate over the related virtual servers
    if [[ -n "$related_virtuals" ]]; then
        IFS=';' read -ra virtual_array <<< "$related_virtuals"
        for virtual in "${virtual_array[@]}"; do
            # Fetch the pool attached to this virtual server using tmsh
            pool=$(tmsh list ltm virtual "$virtual" one-line | grep -o "pool [^ ]*" | awk '{print $2}')
            # Append only the pool name to the pools variable
            if [[ -n "$pool" ]]; then
                pools+="${pool};"
            else
                pools+="NoPool;"
            fi
        done
    fi

    # Add results to the output CSV
    if [[ -z "$related_virtuals" ]]; then
        echo "$server_name,,NoVirtualsFound" >> "$OUTPUT_CSV"
    else
        echo "$server_name,$related_virtuals,$pools" >> "$OUTPUT_CSV"
    fi
done

echo "Processing completed. Output written to: $OUTPUT_CSV"
