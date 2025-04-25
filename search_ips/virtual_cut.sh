#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -i <input_csv_file> -o <output_file>"
    exit 1
}

# Parse command-line arguments
while getopts "i:o:" opt; do
    case $opt in
        i) CSV_FILE="$OPTARG" ;;
        o) OUTPUT_FILE="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if both input and output files are provided
if [[ -z "$CSV_FILE" || -z "$OUTPUT_FILE" ]]; then
    usage
fi

# Check if the input file exists
if [[ ! -f "$CSV_FILE" ]]; then
    echo "Error: Input file '$CSV_FILE' does not exist."
    exit 1
fi

# Clear the output file if it exists
> "$OUTPUT_FILE"

# Read the CSV line by line
while IFS=, read -r f5_pool f5_datagroups; do
    # Skip the header line
    if [[ "$f5_pool" == "Pool" && "$f5_datagroups" == "Datagroups" ]]; then
        continue
    fi

    # Command to list pool members
    echo "Processing pool: $f5_pool" >> "$OUTPUT_FILE"
    pool_members_cmd="tmsh list ltm pool $f5_pool members"
    echo "Running: $pool_members_cmd" >> "$OUTPUT_FILE"
    
    # Execute the command and capture output
    pool_members_output=$(eval "$pool_members_cmd" 2>&1)
    echo "$pool_members_output" >> "$OUTPUT_FILE"

    # Split datagroups by `;` and iterate over them
    IFS=';' read -ra datagroup_array <<< "$f5_datagroups"
    for dg in "${datagroup_array[@]}"; do
        # Command to list datagroup entries
        echo "Processing datagroup: $dg" >> "$OUTPUT_FILE"
        datagroup_cmd="tmsh list ltm data-group internal $dg"
        echo "Running: $datagroup_cmd" >> "$OUTPUT_FILE"
        
        # Execute the command and capture output
        datagroup_output=$(eval "$datagroup_cmd" 2>&1)
        echo "$datagroup_output" >> "$OUTPUT_FILE"
    done

    echo "" >> "$OUTPUT_FILE"
done < "$CSV_FILE"

echo "TMSH command outputs have been written to $OUTPUT_FILE."
