#!/usr/bin/env python3

import json
import argparse

# Function to read the data from the text file
def read_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

# Function to extract the records 
def construct_as3_json(lines,name):
    records = []
    for line in lines:
        # Strip spaces
        line = line.strip()
        #print (line)
        # Check if the line starts with "/Common"
        if line.startswith('"'):
            #print ("on record conditional")
            # Extract the record string before the first " { " 
            record = line.split(' { ')[0].strip('"')
            records.append({"key": record, "value": ""})

    
    #  AS3  structure
    
    as3_data = {
        name: {
            "class": "Data_Group",
            "storageType": "internal",
            "keyDataType": "string",
            "records": records
        }
    }
    return as3_data

# Function to write the AS3 declaration to an output file
def write_as3_json(as3_data, output_file_path):
    with open(output_file_path, 'w') as output_file:
        json.dump(as3_data, output_file, indent=4)
    print("Conversion completed it is saved to", output_file_path)

# Main function
def main():
    #Arguments
    parser=argparse.ArgumentParser(description= 'Convert txt file to AS3')
    parser.add_argument ('-f', '--file', required=True, help= 'Path to the txt file containing the records')
    parser.add_argument ('-n', '--name', required=True, help='Name of the AS3 block')
    args = parser.parse_args()
    
    input_file_path = args.file
    name= args.name
    output_file_path = 'as3_block.json'
    
    lines = read_data(input_file_path)
    as3_data = construct_as3_json(lines,name)
    write_as3_json(as3_data, output_file_path)

if __name__ == "__main__":
    main()
