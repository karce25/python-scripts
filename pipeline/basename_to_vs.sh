#!/bin/bash

# Help function to display usage
show_help() {
  echo "Usage: $0 -i <input_file> -o <output_file>"
  echo ""
  echo "Options:"
  echo "  -i  Specify input CSV file containing basenames."
  echo "  -o  Specify output CSV file for the virtual server list."
  echo ""
  exit 1
}

# Parse arguments
INPUT_FILE=""
OUTPUT_FILE=""

while getopts ":i:o:" opt; do
  case $opt in
    i)
      INPUT_FILE="$OPTARG"
      ;;
    o)
      OUTPUT_FILE="$OPTARG"
      ;;
    *)
      show_help
      ;;
  esac
done

# Check if input and output files are provided
if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FILE" ]]; then
  show_help
fi

# Check if input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Input file $INPUT_FILE not found. Please provide a valid input file."
  exit 1
fi

# Clear/create the output file
echo "BaseName,VirtualServerName" > "$OUTPUT_FILE"

# Read the list of all virtual servers from the BIG-IP
virtual_list=$(tmsh list ltm virtual one-line | awk '{print $3}')

# Loop through each basename in the input CSV file
while IFS= read -r basename; do
  # Search for matching virtual servers
  matches=$(echo "$virtual_list" | grep "^${basename}_")

  if [[ -z "$matches" ]]; then
    # No virtual server found for the basename
    echo "$basename,\"no virtual server with $basename\"" >> "$OUTPUT_FILE"
  else
    # Write each matching virtual server to output
    while IFS= read -r match; do
      echo "$basename,$match" >> "$OUTPUT_FILE"
    done <<< "$matches"
  fi
done < "$INPUT_FILE"

echo "Output written to $OUTPUT_FILE"
