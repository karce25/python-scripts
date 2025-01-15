
# Datagroup converter to AS3 

## Overview
This script read a .txt file containing Datagroups records and converts those records into AS3 format

## Prerequisites

- ``` json ``` library
- ``` argparse ``` library
- A txt file containing only the Data group records

## Usage

1. Create a .txt file with the datagroup records, for example :

```
"string1" { }
"string2" { }
(...)

```
# Running the script

1. Run the script with the following command:
   
 ```
./data_groups_to_as3 -f data.txt -n data_group

```
- `-f` or `--file`: Specifies the path to the input text file that contains the records.
- `-n` or `--name`: Specifies the name of the AS3 block.

# Output

The script generates a json file named as3_block.json

# Example output

```
{
    "test_block": {
        "class": "Data_Group",
        "storageType": "internal",
        "keyDataType": "string",
        "records": [
            {
                "key": "string1",
                "value": ""
            },
            {
                "key": "string2",
                "value": ""
            },
            {
                "key": "string3",
                "value": ""
            }
        ]
    }
}
```





