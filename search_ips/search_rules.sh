#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -i <input_csv> -o <output_csv>"
    exit 1
}

# Parse arguments
while getopts "i:o:" opt; do
    case $opt in
        i)
            input_csv=$OPTARG
            ;;
        o)
            output_csv=$OPTARG
            ;;
        *)
            usage
            ;;
    esac
done

# Check if both input and output arguments are provided
if [[ -z $input_csv || -z $output_csv ]]; then
    usage
fi

# Initialize the output CSV file with new headers
echo "VirtualServerName,iRules,SNAT,Destination,HTTP_Profile" > "$output_csv"

# Read the CSV file line by line (skip the header)
tail -n +2 "$input_csv" | while IFS=, read virtual_server
do
    # Query the virtual server using tmsh
    tmsh_output=$(tmsh list ltm virtual "$virtual_server")

    # Extract the iRules and separate them with semicolons
    irules=$(echo "$tmsh_output" | sed -n '/rules {/,/}/p' | grep -v 'rules {' | grep -v '}' | xargs | tr ' ' ';')

    # Extract the SNAT value (if present)
    snat=$(echo "$tmsh_output" | sed -n '/source-address-translation {/,/}/p' | grep 'type' | awk '{print $2}')
    if [[ -z $snat ]]; then
        snat="None"  # Use "None" if SNAT is not present
    fi

    # Extract the destination value
    destination=$(echo "$tmsh_output" | grep "destination" | awk '{print $2}')
    if [[ -z $destination ]]; then
        destination="None"  # Use "None" if destination is not present
    fi

    # Extract HTTP profile using the targeted command
    profiles_output=$(tmsh list ltm virtual "$virtual_server" profiles)
    http_profiles=$(echo "$profiles_output" | grep -oP '\bhttp\S*' | awk '{print $1}' | xargs | tr ' ' ';')

    if [[ -z $http_profiles ]]; then
        http_profiles="None"  # Use "None" if no HTTP profile is attached
    fi

    # Append the virtual server name, iRules, SNAT value, destination, and HTTP profile to the output CSV
    echo "$virtual_server,\"$irules\",$snat,$destination,\"$http_profiles\"" >> "$output_csv"
done

echo "Processing complete. Output written to $output_csv"
