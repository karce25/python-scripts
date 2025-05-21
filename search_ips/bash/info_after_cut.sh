#!/bin/bash

# Usage
usage() {
    echo "Usage: $0 -i <input_csv> -o <output_csv>"
    exit 1
}

# Argument parsing
while getopts "i:o:" opt; do
    case $opt in
        i) INPUT_CSV="$OPTARG" ;;  # Input CSV
        o) OUTPUT_CSV="$OPTARG" ;; # Output CSV
        *) usage ;;  # Display usage for invalid arguments
    esac
done

# Check if both input and output files are provided
if [ -z "$INPUT_CSV" ] || [ -z "$OUTPUT_CSV" ]; then
    usage
fi

# Start with an empty output file
> "$OUTPUT_CSV"

# Add headers to the CSV
echo "Pool,Target_IP,Port" >> "$OUTPUT_CSV"

# Process each line in the input CSV
tail -n +2 "$INPUT_CSV" | while IFS=',' read -r ASSIGNED_POOLS CURRENT_IP TARGET_IP DATA_GROUPS; do
    # Split assigned pools (space-separated) into an array
    IFS=' ' read -r -a POOLS <<< "$ASSIGNED_POOLS"
    
    # Process each pool in the Assigned Pools column
    for POOL in "${POOLS[@]}"; do
        # List the pool members and capture the details
        POOL_MEMBERS=$(tmsh list ltm pool "$POOL" members)
        
        # Search for the current IP and dynamically capture its port
        POOL_PORT=$(echo "$POOL_MEMBERS" | grep -oP "(?<=${CURRENT_IP}:)\d+")
        
        if [ -n "$POOL_PORT" ]; then
            # Output the pool, target IP, and port as CSV
            echo "$POOL,$TARGET_IP,$POOL_PORT" >> "$OUTPUT_CSV"
        else
            echo "# WARNING: Current IP ($CURRENT_IP) not found in pool $POOL" >> "$OUTPUT_CSV"
        fi
    done
done

echo "CSV generation completed: $OUTPUT_CSV"
