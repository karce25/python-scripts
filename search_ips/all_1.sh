#!/bin/bash
#Added rule check functionality
###############################################
# Display a usage message if arguments are missing
###############################################
usage() {
    echo "Usage: $0 -f <input_csv>"
    echo "    -f: Specify the CSV file containing IP addresses."
    exit 1
}
###############################################
# Parse command-line arguments
###############################################
CSV_FILE=""
while getopts "f:" opt; do
    case "$opt" in
        f)
            CSV_FILE=$OPTARG
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
# Specify the output file
OUTPUT_FILE="output.txt"
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
        # Check if the IP appears in the records field
        if (match($0, ip)) {
            print "Datagroup where node is found: " datagroup
        }
    }')
    if [ -z "$MATCHED_DATAGROUPS" ]; then
        echo -e "No datagroups found containing node IP: '$IP'\n" >> "$OUTPUT_FILE"
    else
        echo -e "$MATCHED_DATAGROUPS\n" >> "$OUTPUT_FILE"
    fi
}

###############################################
# Function to fetch rules applied to a virtual server
###############################################
fetch_rules_for_virtual_server() {
    VS_NAME="$1"  # Virtual server name
    RULES=$(tmsh list ltm virtual "$VS_NAME" | awk '/rules \{/ {getline; gsub(/[{}]/, "", $0); print}' | xargs)

    if [ -n "$RULES" ]; then
        echo "Rules applied to Virtual Server '$VS_NAME': $RULES" >> "$OUTPUT_FILE"
    else
        echo "No Rules applied to Virtual Server '$VS_NAME'" >> "$OUTPUT_FILE"
    fi
}

###############################################
# Function to process each pool
###############################################
process_pool() {
    POOL_NAME="$1"
    echo -e "\n-----------------------------------------" >> "$OUTPUT_FILE"
    echo -e "Processing Pool: $POOL_NAME\n" >> "$OUTPUT_FILE"
    # Extract base name of the pool (everything before "_")
    BASE_NAME=$(echo "$POOL_NAME" | cut -d'_' -f1)
    echo -e "Base Name of the Pool: $BASE_NAME\n" >> "$OUTPUT_FILE"

    ########################################################
    # Search for base name matches in datagroups
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
        echo "No relevant datagroup entries found for Base Name: '$BASE_NAME'" >> "$OUTPUT_FILE"
    else
        echo -e "$FOUND_DATAGROUPS\n" >> "$OUTPUT_FILE"
    fi

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
    }' | sort | uniq)  # Deduplicate the extracted virtual servers using `sort | uniq`
    if [ -z "$FIRST_PARTS" ]; then
        echo -e "No First Parts Extracted from matching records.\n" >> "$OUTPUT_FILE"
    else
        echo -e "Extracted Virtual servers:\n$FIRST_PARTS\n" >> "$OUTPUT_FILE"
    fi

    ########################################################
    # Perform extended search using extracted first parts
    ########################################################
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
            # Match records explicitly containing the first part
            if (match($0, part)) {
                print "Found in Datagroup: " datagroup
                print $0
            }
        }')
        if [ -z "$EXTENDED_SEARCH" ]; then
            echo -e "No matching records found for: '$PART'\n" >> "$OUTPUT_FILE"
        else
            echo -e "Extended Search Results:\n$EXTENDED_SEARCH\n" >> "$OUTPUT_FILE"
        fi

        ############################################################
        # Extract pools affected from the search results
        ############################################################
        echo -e "Processing Pools Affected for: '$PART'\n" >> "$OUTPUT_FILE"
        POOLS_AFFECTED=$(echo "$EXTENDED_SEARCH" | awk '
        {
            # Match for valid pools in "/Common/<pool_name>" patterns at the end of the line
            if (match($0, /\s\/Common[^ ]+/)) {
                last_part = substr($0, RSTART, RLENGTH)
                gsub(/[\{\}\"]/,"",last_part)  # Clean quotes and brackets
                print last_part
            }
        }' | sort | uniq)
        if [ -n "$POOLS_AFFECTED" ]; then
            echo -e "Pools Affected by '$PART':\n$POOLS_AFFECTED\n" >> "$OUTPUT_FILE"
        else
            echo -e "No Pools Affected for '$PART'\n" >> "$OUTPUT_FILE"
        fi
    done

    ########################################################
    # Search for virtual servers using the pool
    ########################################################
    VS_NAME=$(tmsh list ltm virtual one-line | grep " pool $POOL_NAME " | awk '{print $3}')
    if [ -z "$VS_NAME" ]; then
        echo "No Virtual Server Found for Pool: $POOL_NAME" >> "$OUTPUT_FILE"
    else
        echo "Virtual Server Attached to '$POOL_NAME': $VS_NAME" >> "$OUTPUT_FILE"
        # Fetch and print rules for the virtual server
        fetch_rules_for_virtual_server "$VS_NAME"
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
    POOL_NAMES=$(tmsh list ltm pool one-line | grep "$IP" | awk '{print $3}')
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
    find_and_format_output "$IP"
done < "$CSV_FILE"
echo -e "\nOutput has been written to $OUTPUT_FILE"
