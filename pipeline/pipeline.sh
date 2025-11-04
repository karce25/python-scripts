#!/bin/bash

# Exit immediately if a pipeline returns a non-zero status
set -e

# Ensure the right number of arguments are passed (should be 3)
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <final_output_file> <snat_pool> <x_forwarded_for>"
    echo "Example: $0 commands_output.txt NWA1_F5L1A_UPLK_snat_pool rhe_x-forwarded-for"
    exit 1
fi

# Assign arguments to variables for simplicity and readability
FINAL_OUTPUT_FILE=$1
SNAT_POOL=$2
X_FORWARDED_FOR=$3

echo "==================== WORKFLOW START ===================="

# Step 1: Run virtual_data_group_column_separator.sh
echo "Step 1: Separating Virtual Data Groups from input file..."
echo "Processing input file 'output_research.csv'..."
./virtual_data_group_column_separator.sh -i output_research.csv -o basenames_list.csv
echo "--------------------------------------------------------"

# Step 2: Run basenames_to_vs.sh
echo "Step 2: Searching Virtual Servers with basenames..."
echo "Processing input file 'basenames_list.csv'..."
./basenames_to_vs.sh -i basenames_list.csv -o virtual_list_from_basenames.csv
echo "--------------------------------------------------------"

# Step 3: Run virtual_list_final.sh
echo "Step 3: Creating Virtual List from basenames found..."
echo "Processing input file 'virtual_list_from_basenames.csv'..."
./virtual_list_final.sh -i virtual_list_from_basenames.csv -o virtual_list.csv
echo "--------------------------------------------------------"

# Step 4: Run snat_enable.sh
echo "Step 4: Creating tmsh SNAT enable commands for Virtual List..."
echo "Using SNAT Pool: $SNAT_POOL"
echo "Using X-Forwarded-For: $X_FORWARDED_FOR"
echo "Processing input file 'virtual_list.csv'..."
./snat_enable.sh -i virtual_list.csv -s "$SNAT_POOL" -r "$X_FORWARDED_FOR" -o "$FINAL_OUTPUT_FILE"
echo "--------------------------------------------------------"

# Workflow completed
echo "=================== WORKFLOW COMPLETE =================="
echo "Final output file: $FINAL_OUTPUT_FILE"
