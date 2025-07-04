#!/bin/bash

###############################################
# Display a usage message if arguments are missing
###############################################
usage() {
    echo "Usage: $0 -f <input_csv> [-o <output_file>]"
    echo "    -i: Specify the CSV file containing IP addresses."
    echo "    -o: Specify the output file (default: output.txt)."
    exit 1
}

###############################################
# Parse command-line arguments
###############################################
CSV_FILE=""
OUTPUT_FILE="output.txt"  # Default output file
while getopts "i:o:" opt; do
    case "$opt" in
        i)
            CSV_FILE=$OPTARG
            ;;
        o)
            OUTPUT_FILE=$OPTARG
            ;;
        *)
            usage
            ;;
    esac
done

# Ensure the CSV file is provided
if [ -z "$CSV_FILE" ]; then
    usage
fi

# Ensure the specified file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: File '$CSV_FILE' not found."
    exit 1
fi

# Ensure tmsh command is available
if ! command -v tmsh &> /dev/null; then
    echo "Error: TMSH command not found. Ensure this script runs on a BIG-IP system."
    exit 1
fi

# Clear or create the output file
> "$OUTPUT_FILE"
echo -e "\nPlease wait while gathering info...\n"

###########################################
# Function to search datagroups where the node IP is found
###########################################
search_datagroups_for_ip() {
    IP="$1"
    echo -e "\nSearching datagroups for Node IP: '$IP'...\n" >> "$OUTPUT_FILE"
    MATCHED_DATAGROUPS=$(tmsh list ltm data-group internal | awk -v ip="$IP" '
    BEGIN {datagroup=""}
    {
        # Capture the name of the current datagroup
        if ($0 ~ /ltm data-group internal/) {
            datagroup = $4
        }
        # Check if the IP appears as a full match
        if (match($0, "(^|[^0-9])" ip "([^0-9]|$)")) {
            print "Datagroup where node is found: " datagroup
        }
    }')

    if [ -z "$MATCHED_DATAGROUPS" ]; then
        echo -e "No datagroups found containing node IP: '$IP'\n" >> "$OUTPUT_FILE"
        return
    fi
    echo -e "$MATCHED_DATAGROUPS\n" >> "$OUTPUT_FILE"
}

###############################################
# Function to process each pool
###############################################
process_pool() {
    POOL_NAME="$1"
    echo -e "\n-----------------------------------------" >> "$OUTPUT_FILE"
    echo -e "Processing Pool: $POOL_NAME\n" >> "$OUTPUT_FILE"
    # Extract base name of the pool
    BASE_NAME=$(echo "$POOL_NAME" | cut -d'_' -f1)
    echo -e "Base Name of the Pool: $BASE_NAME\n" >> "$OUTPUT_FILE"

    ########################################################
    # Search for base name matches in all datagroups
    ########################################################
    echo -e "Searching data groups for Base Name: '$BASE_NAME'...\n" >> "$OUTPUT_FILE"
    FOUND_DATAGROUPS=$(tmsh list ltm data-group internal | awk -v base_name="$BASE_NAME" '
    BEGIN {datagroup=""}
    {
        # Capture the name of the current datagroup
        if ($0 ~ /ltm data-group internal/) {
            datagroup = $4  # Get the datagroup name
        }
        # Match lines explicitly containing "/Common/<base_name>" in the correct context
        if (match($0, "/Common/"base_name"[^ ]*")) {
            print "Found in Datagroup: " datagroup
            print $0
        }
    }')

    if [ -z "$FOUND_DATAGROUPS" ]; then
        echo -e "No relevant data group entries found for Base Name: '$BASE_NAME'\n" >> "$OUTPUT_FILE"
        return
    fi
    echo -e "$FOUND_DATAGROUPS\n" >> "$OUTPUT_FILE"

    ########################################################
    # Extract the first parts of matched records
    ########################################################
    echo -e "Extracting First Parts of Matching Records...\n" >> "$OUTPUT_FILE"
    FIRST_PARTS=$(echo "$FOUND_DATAGROUPS" | awk -F':' '
    {
        # Extract the first part of the record (before ":")
        if ($1 ~ /\/Common\//) {
            split($1, parts, " ");
            print parts[1]
        }
    }' | sort | uniq)

    if [ -z "$FIRST_PARTS" ]; then
        echo -e "No First Parts Extracted from matching records.\n" >> "$OUTPUT_FILE"
        return
    fi
    echo -e "Extracted Virtual servers:\n$FIRST_PARTS\n" >> "$OUTPUT_FILE"

    ############################################################
    # Perform extended search using extracted first parts
    ############################################################
    echo -e "Performing Extended Search for Matched Virtual servers...\n" >> "$OUTPUT_FILE"
    echo "$FIRST_PARTS" | while read -r PART; do
        echo -e "Searching for records containing Virtual server '$PART'...\n" >> "$OUTPUT_FILE"
        EXTENDED_SEARCH=$(tmsh list ltm data-group internal | awk -v part="$PART" '
        BEGIN {datagroup=""}
        {
            # Capture the name of the current datagroup
            if ($0 ~ /ltm data-group internal/) {
                datagroup = $4
            }
            # Match records explicitly containing the part
            if (match($0, "(^|[^0-9])" part "([^0-9]|$)")) {
                print "Found in Datagroup: " datagroup
                print $0
            }
        }')

        if [ -z "$EXTENDED_SEARCH" ]; then
            echo -e "No matching records found for: '$PART'\n" >> "$OUTPUT_FILE"
            continue
        fi
        echo -e "Extended Search Results:\n$EXTENDED_SEARCH\n" >> "$OUTPUT_FILE"
    done

    ###########################################
    # Search for virtual servers using the pool
    ###########################################
    VS_NAME=$(tmsh list ltm virtual one-line | grep " pool $POOL_NAME " | awk '{print $3}')
    if [ -z "$VS_NAME" ]; then
        echo -e "No Virtual Server Found for Pool: $POOL_NAME\n" >> "$OUTPUT_FILE"
    else
        echo -e "Virtual Server Attached to '$POOL_NAME': $VS_NAME\n" >> "$OUTPUT_FILE"
    fi
}

###############################################
# Function to process each IP address
###############################################
find_and_format_output() {
    IP="$1"
    echo -e "\n=========================================" >> "$OUTPUT_FILE"
    echo -e "Processing IP: $IP\n" >> "$OUTPUT_FILE"

    # Find datagroups containing the node IP
    search_datagroups_for_ip "$IP"

    # Find pools where the IP is a member
    POOL_NAMES=$(tmsh list ltm pool one-line | awk -v ip="$IP" '$0 ~ "(^|[^0-9])" ip "([^0-9]|$)" {print $3}')
    if [ -z "$POOL_NAMES" ]; then
        echo -e "No Pools Found for IP: $IP\n" >> "$OUTPUT_FILE"
    else
        echo -e "Pools Associated with the IP:\n" >> "$OUTPUT_FILE"
        echo "$POOL_NAMES" | while read -r POOL_NAME; do
            echo -e "- $POOL_NAME\n" >> "$OUTPUT_FILE"
            process_pool "$POOL_NAME"
        done
    fi
    echo -e "=========================================\n" >> "$OUTPUT_FILE"
}

##########################################################
# Process each IP address in the provided CSV file
##########################################################
while IFS=, read -r IP
do
    # Validate the format of the IP address
    if [[ "$IP" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
        find_and_format_output "$IP"
    else
        echo "Invalid IP format: $IP. Skipping..." >> "$OUTPUT_FILE"
    fi
done < "$CSV_FILE"

echo -e "\nOutput has been written to $OUTPUT_FILE"
