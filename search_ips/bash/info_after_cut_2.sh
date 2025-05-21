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
echo "Pool,Target_IP,Port,Status" >> "$OUTPUT_CSV"

# Process each line in the input CSV
tail -n +2 "$INPUT_CSV" | while IFS=',' read -r ASSIGNED_POOLS CURRENT_IP TARGET_IP DATA_GROUPS; do
    # Split assigned pools (space-separated) into an array
    IFS=' ' read -r -a POOLS <<< "$ASSIGNED_POOLS"
    
    # Process each pool in the Assigned Pools column
    for POOL in "${POOLS[@]}"; do
        # List the pool members and capture the details
        POOL_MEMBERS=$(tmsh list ltm pool "$POOL" members)
        
        # Search for the target IP and dynamically capture its port
        POOL_PORT=$(echo "$POOL_MEMBERS" | grep -oP "(?<=${TARGET_IP}:)\d+")
        
        if [ -n "$POOL_PORT" ]; then
            # Get the status of the pool member (e.g., enabled or disabled)
            MEMBER_STATUS=$(echo "$POOL_MEMBERS" | grep -A 1 "${TARGET_IP}:${POOL_PORT}" | grep -oP '(?<=status ).*' | head -n 1)
            
            # Fallback if no status is found
            if [ -z "$MEMBER_STATUS" ]; then
                MEMBER_STATUS="UNKNOWN"
            fi
            
            # Output the pool, target IP, port, and status as CSV
            echo "$POOL,$TARGET_IP,$POOL_PORT,$MEMBER_STATUS" >> "$OUTPUT_CSV"
        else
            echo "# WARNING: Target IP ($TARGET_IP) not found in pool $POOL" >> "$OUTPUT_CSV"
        fi
    done
done

echo "Enhanced CSV generation completed: $OUTPUT_CSV"
