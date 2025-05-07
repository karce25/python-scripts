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
echo "ServerName,RelatedVirtual,Pool,SNAT_Pool,PoolMembers,PoolMemberStatus" > "$OUTPUT_CSV"

# Process each virtual server in the input CSV
tail -n +2 "$INPUT_CSV" | while IFS=, read -r server_name; do
    # Initialize variables
    base_name=""
    related_virtual=""
    first_pool=""
    pool_members=""
    pool_member_status=""
    snat_pool=""

    # Step 1: Grab the base name
    base_name=$(echo "$server_name" | sed -E 's/_[^_]+$//') # Extract base name

    # Step 2: Search for related virtual servers
    related_virtual=$(tmsh list ltm virtual | grep -o "${base_name}_[^ ]*" | grep -v "$server_name" | head -n 1)
    if [[ -z "$related_virtual" ]]; then
        related_virtual="NoRelatedVirtual"
        first_pool="NoPool"
        snat_pool="NoSNAT_Pool"
        pool_members="NoMembers"
        pool_member_status="NoStatus"
        echo "$server_name,$related_virtual,$first_pool,$snat_pool,$pool_members,$pool_member_status" >> "$OUTPUT_CSV"
        continue
    fi

    # Step 3: Grab the pool from the related virtual server
    related_virtual_config=$(tmsh list ltm virtual "$related_virtual" 2>/dev/null)
    first_pool=$(echo "$related_virtual_config" | grep -oP "pool \K[^ ]+" | head -n 1)
    if [[ -z "$first_pool" ]]; then
        first_pool="NoPool"
        pool_members="NoMembers"
        pool_member_status="NoStatus"
    else
        # Step 4: Grab the pool members from the first pool
        pool_members=$(tmsh list ltm pool "$first_pool" members 2>/dev/null | grep -oP "address \K[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | tr '\n' ';')
        pool_members=$(echo "$pool_members" | sed 's/;$//')  # Remove trailing semicolon, if any
        pool_members=${pool_members:-"NoMembers"}  # Default if no members found

        # Step 5: Check pool member status
        pool_member_status_output=$(tmsh show ltm pool "$first_pool" members 2>/dev/null)
        if [[ -n "$pool_member_status_output" ]]; then
            # Loop through each member and extract status details
            while IFS= read -r member_line; do
                if [[ "$member_line" == *"Ltm::Pool Member"* ]]; then
                    member_ip=$(echo "$member_line" | grep -oP "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
                fi
                if [[ "$member_line" == *"Availability"* ]]; then
                    availability=$(echo "$member_line" | grep -oP "Availability\s*:\s*\K[^\n]+")
                fi
                if [[ "$member_line" == *"State"* ]]; then
                    state=$(echo "$member_line" | grep -oP "State\s*:\s*\K[^\n]+")
                fi
                if [[ "$member_line" == *"Reason"* ]]; then
                    reason=$(echo "$member_line" | grep -oP "Reason\s*:\s*\K[^\n]+")
                fi

                # Add the parsed output for each pool member
                if [[ -n "$member_ip" && -n "$availability" && -n "$state" ]]; then
                    pool_member_status+="${member_ip} (Availability: ${availability}, State: ${state}, Reason: ${reason}); "
                    member_ip=""
                    availability=""
                    state=""
                    reason=""
                fi
            done <<< "$pool_member_status_output"

            # Remove trailing semicolon and space, if any
            pool_member_status=$(echo "$pool_member_status" | sed 's/; $//')
        else
            pool_member_status="NoStatus"
        fi
    fi

    # Step 6: Grab the SNAT pool using the specific command
    virtual_snat_config=$(tmsh list ltm virtual "$related_virtual" source-address-translation { pool } 2>/dev/null)
    snat_pool=$(echo "$virtual_snat_config" | grep -oP "pool \K[^ ]+" || echo "NoSNAT_Pool")
    snat_pool=${snat_pool:-"NoSNAT_Pool"}  # Default to "NoSNAT_Pool" if none found

    # Write the results to the output CSV
    echo "$server_name,$related_virtual,$first_pool,$snat_pool,$pool_members,$pool_member_status" >> "$OUTPUT_CSV"
done

echo "Processing completed. Output written to: $OUTPUT_CSV"
