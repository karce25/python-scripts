#!/bin/bash

# Usage function to display help message
usage() {
  echo "Usage: $0 -i <input_file> -o <output_file>"
  echo "    -i  Path to the input CSV file"
  echo "    -o  Path to the output CSV file"
  exit 1
}

# Parse the command-line arguments
while getopts ":i:o:" opt; do
  case $opt in
    i) input_file="$OPTARG" ;;
    o) output_file="$OPTARG" ;;
    *) usage ;;
  esac
done

# Ensure both input and output files are provided
if [ -z "$input_file" ] || [ -z "$output_file" ]; then
  usage
fi

# Check if the input file exists
if [ ! -f "$input_file" ]; then
  echo "Error: Input file '$input_file' does not exist."
  exit 1
fi

# Extract the VirtualServerName column, remove duplicates, and save to the output file
awk -F ',' '
BEGIN { OFS="," }
{
  if (NR == 1) {
    for (i = 1; i <= NF; i++) {
      if ($i == "VirtualServerName") {
        column_number = i
        print "VirtualServerName" > "'"$output_file"'"
      }
    }
  } else {
    if (column_number && $column_number != "" && $column_number !~ /no virtual server/) {
      print $column_number
    }
  }
}' "$input_file" | sort -u >> "$output_file"

echo "Processing complete. Unique VirtualServerName values saved to $output_file."
