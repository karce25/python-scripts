#!/bin/bash

# Usage
usage() {
    echo "Usage: $0 -i <input_csv> -o <output_file>"
    exit 1
}

# Argument parsing
while getopts "i:o:" opt; do
    case $opt in
        i) CSV_FILE="$OPTARG" ;;  # Input CSV
        o) OUTPUT_FILE="$OPTARG" ;; # Output file
        *) usage ;;  # Display usage for invalid arguments
    esac
done

# Check if both input and output files are provided
if [ -z "$CSV_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    usage
fi

# Rollback commands file
ROLLBACK_FILE="${OUTPUT_FILE%.*}_rollback.txt"

# Start with empty output files
> "$OUTPUT_FILE"
> "$ROLLBACK_FILE"

#Echo to inform user of the script start

echo "Starting cutover script generation..."

# Process each line in the CSV 
tail -n +2 "$CSV_FILE" | while IFS=',' read -r ASSIGNED_POOLS CURRENT_IP TARGET_IP DATA_GROUPS; do

    # Split assigned pools (space-separated) into an array
    IFS=' ' read -r -a POOLS <<< "$ASSIGNED_POOLS"

    # Split data groups (semicolon-separated) into an array
    IFS=';' read -r -a DATA_GROUP_ENTRIES <<< "$DATA_GROUPS"

    # Variables to store rollback details for data groups
    DECLARED_PREFIX=""
    DECLARED_PORT=""

    # Process each pool in Assigned Pools column
    for POOL in "${POOLS[@]}"; do
        # List the pool members and capture the details
        POOL_MEMBERS=$(tmsh list ltm pool "$POOL" members)

        # Add a comment indicating pool configuration
        echo "# Configuration for pool: $POOL" >> "$OUTPUT_FILE"

        # Search for the current IP and dynamically capture its port
        POOL_PORT=$(echo "$POOL_MEMBERS" | grep -oP "(?<=${CURRENT_IP}:)\d+")
        if [ -n "$POOL_PORT" ]; then
            # Commands 
            echo "# Add new member to $POOL" >> "$OUTPUT_FILE"
            echo "tmsh modify ltm pool $POOL members add { $TARGET_IP:$POOL_PORT { address $TARGET_IP } }" >> "$OUTPUT_FILE"

            echo "# Disable current member in $POOL" >> "$OUTPUT_FILE"
            echo "tmsh modify ltm pool $POOL members modify { $CURRENT_IP:$POOL_PORT { session user-disabled } }" >> "$OUTPUT_FILE"

            # Rollback commands 
            echo "# Rollback commands for pool: $POOL" >> "$ROLLBACK_FILE"
            echo "tmsh modify ltm pool $POOL members modify { $CURRENT_IP:$POOL_PORT { session user-enabled } }" >> "$ROLLBACK_FILE"
            echo "tmsh modify ltm pool $POOL members modify { $TARGET_IP:$POOL_PORT { session user-disabled } }" >> "$ROLLBACK_FILE"
        else
            echo "# WARNING: Current IP ($CURRENT_IP) not found in pool $POOL" >> "$OUTPUT_FILE"
            echo "# WARNING: Current IP ($CURRENT_IP) not found in pool $POOL" >> "$ROLLBACK_FILE"
        fi
    done

    # Process each data group in Data Groups
    for DATA_GROUP in "${DATA_GROUP_ENTRIES[@]}"; do
        # Comment
        echo "# Modify Data group: $DATA_GROUP" >> "$OUTPUT_FILE"

        # List the data group records and search for the Current IP
        DG_RECORDS=$(tmsh list ltm data-group internal "$DATA_GROUP")

        # Search for the data group record containing the Current IP
        DG_ENTRY=$(echo "$DG_RECORDS" | grep -oP "\".*${CURRENT_IP}:\d+.*\"")
        
        if [ -n "$DG_ENTRY" ]; then
            # Remove extra quotes from DG_ENTRY 
            DG_ENTRY=$(echo "$DG_ENTRY" | sed 's/^"//;s/"$//')  # Remove leading and trailing quotes

            # Extract the prefix  and port from the data group entry
            PREFIX=$(echo "$DG_ENTRY" | awk '{print $1}')
            DG_PORT=$(echo "$DG_ENTRY" | grep -oP "(?<=${CURRENT_IP}:)\d+")

            # Save extracted prefix and port for rollback
            DECLARED_PREFIX="$PREFIX"
            DECLARED_PORT="$DG_PORT"

            # Commands
            echo "tmsh modify ltm data-group internal $DATA_GROUP records add { \"$PREFIX $TARGET_IP:$DG_PORT\" { } }" >> "$OUTPUT_FILE"
            echo "tmsh modify ltm data-group internal $DATA_GROUP records delete { \"$PREFIX $CURRENT_IP:$DG_PORT\" }" >> "$OUTPUT_FILE"
        else
            # Handle missing entries with warnings and placeholders
            echo "# WARNING: Current IP ($CURRENT_IP) not found in data group $DATA_GROUP" >> "$OUTPUT_FILE"
            DECLARED_PREFIX="<UNKNOWN_PREFIX>"
            DECLARED_PORT="<UNKNOWN_PORT>"
        fi

        # Rollback commands
        echo "# Rollback commands for data group: $DATA_GROUP" >> "$ROLLBACK_FILE"
        echo "tmsh modify ltm data-group internal $DATA_GROUP records delete { \"$DECLARED_PREFIX $TARGET_IP:$DECLARED_PORT\" }" >> "$ROLLBACK_FILE"
        echo "tmsh modify ltm data-group internal $DATA_GROUP records add { \"$DECLARED_PREFIX $CURRENT_IP:$DECLARED_PORT\" { } }" >> "$ROLLBACK_FILE"
    done
done
