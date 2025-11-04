#!/bin/bash

# Function to display usage of the script
usage() {
    echo "Usage: $0 -i <input_file> -o <output_file>"
    exit 1
}

# Parse command-line arguments
while getopts "i:o:" opt; do
    case $opt in
        i) input_file="$OPTARG" ;;
        o) output_file="$OPTARG" ;;
        *) usage ;;
    esac
done

# Ensure both input and output files are provided
if [[ -z "$input_file" || -z "$output_file" ]]; then
    usage
fi

# Temporary file to hold intermediate results
tmp_file="temp_file.txt"

# Check if input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: Input file '$input_file' does not exist."
    exit 1
fi

# Extract the header row to identify the target column index for "Virtual servers from datagroups"
header=$(head -1 "$input_file")
col_number=$(echo "$header" | awk -F',' '{
    for (i = 1; i <= NF; i++) {
        if ($i ~ /Virtual servers from datagroups/) {
            print i;
            exit;
        }
    }
}')

# Check if the column "Virtual servers from datagroups" is found
if [[ -z "$col_number" ]]; then
    echo "Error: Could not find the column 'Virtual servers from datagroups' in the input file."
    exit 1
fi

# Extract matching entries from the target column
tail -n +2 "$input_file" | awk -F',' -v col="$col_number" '{
    n = split($col, values, "\"");  # Split by double quotes
    for (i = 1; i <= n; i++) {
        if (values[i] ~ /\/Common\//) {  # Find strings with "/Common/"
            print values[i];
        }
    }
}' > "$tmp_file"


awk -F'/Common/' '{ print $2 }' "$tmp_file" | \
    sed 's/[[:space:]]*$//' | \
    sed 's/;$//' | \
    sed 's/^ *//;s/ *$//' | \
    sort -u | \
    sed '/^$/d' > "$output_file"  # Remove any blank lines

# Clean up temporary file
rm -f "$tmp_file"

# Done
echo "Processing complete. Output saved to '$output_file'."
