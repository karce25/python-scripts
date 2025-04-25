#!/bin/bash

# Input CSV file that contains Virtual Server names and Data Groups
INPUT_CSV="input.csv"

# Output file
OUTPUT_FILE="f5_virtuals_details.txt"

# Ensure the input file exists
if [[ ! -f "$INPUT_CSV" ]]; then
    echo "Input CSV file ($INPUT_CSV) not found. Exiting."
    exit 1
fi

# Start writing to the output file
echo "F5 Virtual Servers, Pools, Pool Members, and Data Groups" > "$OUTPUT_FILE"
echo "=========================================================" >> "$OUTPUT_FILE"

# Parse the CSV file line by line
while IFS=',' read -r virtual_server data_groups; do
    # Trim whitespace for virtual server
    virtual_server=$(echo "$virtual_server" | xargs)

    echo "Processing Virtual Server: $virtual_server" >> "$OUTPUT_FILE"

    # Step 1: Get Virtual Server Details
    vs_details=$(tmsh list ltm virtual "$virtual_server" one-line 2>/dev/null)
    if [[ -z "$vs_details" ]]; then
        echo " - Virtual Server not found: $virtual_server" >> "$OUTPUT_FILE"
        continue
    fi

    echo " - Virtual Server Details: $vs_details" >> "$OUTPUT_FILE"

    # Get associated pool and destination
    pool=$(echo "$vs_details" | grep -oP 'pool \S+' | awk '{print $2}')
    destination=$(echo "$vs_details" | grep -oP 'destination \S+' | awk '{print $2}')

    echo " - Pool: $pool" >> "$OUTPUT_FILE"
    echo " - Destination: $destination" >> "$OUTPUT_FILE"

    # Step 2: Get Pool Members if a pool is associated
    if [[ -n "$pool" ]]; then
        echo "   - Retrieving Pool Members for $pool..." >> "$OUTPUT_FILE"
        pool_members=$(tmsh list ltm pool "$pool" members one-line 2>/dev/null | grep -oP 'members \S+' | awk '{print $2}')
        if [[ -z "$pool_members" ]]; then
            echo "   - No members found for pool: $pool" >> "$OUTPUT_FILE"
        else
            echo "   - Pool Members: $pool_members" >> "$OUTPUT_FILE"
        fi
    else
        echo "   - No pool associated with virtual server: $virtual_server" >> "$OUTPUT_FILE"
    fi

    # Step 3: Handle multiple data groups in the same cell
    if [[ -n "$data_groups" ]]; then
        echo "   - Retrieving Data Group Records..." >> "$OUTPUT_FILE"

        # Split the data groups by the `;` delimiter and process each one
        IFS=';' read -ra dg_array <<< "$data_groups"
        for data_group in "${dg_array[@]}"; do
            data_group=$(echo "$data_group" | xargs)  # Trim whitespace
            echo "     - Processing Data Group: $data_group" >> "$OUTPUT_FILE"

            dg_details=$(tmsh list ltm data-group internal "$data_group" 2>/dev/null)
            if [[ -z "$dg_details" ]]; then
                echo "       - Data Group not found: $data_group" >> "$OUTPUT_FILE"
            else
                echo "       - Data Group Records:" >> "$OUTPUT_FILE"
                echo "$dg_details" | sed 's/^/          /' >> "$OUTPUT_FILE"  # Indent the records
            fi
        done
    else
        echo "   - No data group specified for virtual server: $virtual_server" >> "$OUTPUT_FILE"
    fi

done < "$INPUT_CSV"

# Completion message
echo "Data has been written to $OUTPUT_FILE"
