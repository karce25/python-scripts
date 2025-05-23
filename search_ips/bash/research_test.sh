#!/bin/bash
###############################################
# Display a usage message if arguments are missing
###############################################
usage() {
    echo "Usage: $0 -f <input_csv> [-o <output_file>]"
    echo "    -f: Specify the CSV file containing IP addresses."
    echo "    -o: (Optional) Specify the output file. Defaults to 'output.txt'."
    exit 1
}

###############################################
# Parse command-line arguments
###############################################
CSV_FILE=""
OUTPUT_FILE="output.txt"  # Default output file
while getopts "f:o:" opt; do
    case "$opt" in
        f)
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
        if ($0 ~ /ltm data-group internal/) {
            datagroup = $4
        }
        if (match($0, "\\b"ip"\\b")) {
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
    BASE_NAME=$(echo "$POOL_NAME" | cut -d'_' -f1)
    echo -e "Base Name of the Pool: $BASE_NAME\n" >> "$OUTPUT_FILE"
    FOUND_DATAGROUPS=$(tmsh list ltm data-group internal | awk -v base_name="$BASE_NAME" '
    BEGIN {datagroup=""}
    {
        if ($0 ~ /ltm data-group internal/) {
            datagroup = $4
        }
        if (match($0, "/Common/"base_name"[^ ]*")) {
            print "Found in Datagroup: " datagroup
            print $0
        }
    }')
    if [ -z "$FOUND_DATAGROUPS" ]; then
        echo -e "No relevant datagroup entries found for Base Name: '$BASE_NAME'\n" >> "$OUTPUT_FILE"
        return
    fi
    echo -e "$FOUND_DATAGROUPS\n" >> "$OUTPUT_FILE"

    FIRST_PARTS=$(echo "$FOUND_DATAGROUPS" | awk -F':' '
    {
        if ($1 ~ /\/Common\//) {
            split($1, parts, " ");
            print parts[1]
        }
    }' | sort | uniq)
    if [ -z "$FIRST_PARTS" ]; then
        echo -e "No Virtual Servers Extracted from matching records.\n" >> "$OUTPUT_FILE"
        return
    fi
    echo -e "Extracted Virtual Servers:\n$FIRST_PARTS\n" >> "$OUTPUT_FILE"

    echo -e "Performing Extended Search for Matched Virtual Servers...\n" >> "$OUTPUT_FILE"
    echo "$FIRST_PARTS" | while read -r PART; do
        EXTENDED_SEARCH=$(tmsh list ltm data-group internal | awk -v part="$PART" '
        BEGIN {datagroup=""}
        {
            if ($0 ~ /ltm data-group internal/) {
                datagroup = $4
            }
            if (match($0, part)) {
                print "Found in Datagroup: " datagroup
                print $0
            }
        }')
        if [ -z "$EXTENDED_SEARCH" ]; then
            echo -e "No matching records found for: '$PART'\n" >> "$OUTPUT_FILE"
            continue
        fi
        echo -e "Extended Search Results:\n$EXTENDED_SEARCH\n" >> "$OUTPUT_FILE"

        POOLS_AFFECTED=$(echo "$EXTENDED_SEARCH" | awk '
        {
            if (match($0, /\s\/Common[^ ]+(\s|\})?/)) {
                last_part = substr($0, RSTART, RLENGTH)
                gsub(/[\{\}\"]/,"",last_part)
                print last_part
            }
        }' | sort | uniq)
        if [ -n "$POOLS_AFFECTED" ]; then
            echo -e "Pools Affected by: '$PART':\n$POOLS_AFFECTED\n" >> "$OUTPUT_FILE"
        else
            echo -e "No Pools Affected for: '$PART'\n" >> "$OUTPUT_FILE"
        fi
    done

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
    search_datagroups_for_ip "$IP"
    POOL_NAMES=$(tmsh list ltm pool one-line | awk -v ip="$IP" '$0 ~ "\\b"ip"\\b" {print $3}')
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
