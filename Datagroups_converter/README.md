
# Datagroup converter to AS3 

## Overview
This script read a .txt file containing Datagroups records and converts those records into AS3 format

## Prerequisites

- ``` requests ``` library
- A CSV file containing the IP addresses or hostnames of the BIG-IP devices
- Sets common credentials (username and password) inside the python script
```
username = 'user'
password = 'password'
endpoint = '/mgmt/tm/ltm/virtual-address?%24select=address'

```

## Usage

Create a CSV file with the following format (could be either hostname or IP address) :

```
ip_address
10.10.10.10
10.10.10.11

```
```
ip_address
bigiptest.local
bigiptest1.local
```

# Running the script

./virtual_address.py -file bigips.csv

# Output

The script generates a CSV file named all_virtual_addresses.csv in the same directory as the script. This file contains the virtual addresses extracted from each BIG-IP device

# Example output

```
BIG-IP-MGMT,Virtual Address
10.10.10.10,10.20.20.20
10.10.10.10,10.20.20.104
10.10.10.11,10.30.30.64

```

# Notes

- Security Warning: The script uses verify=False to disable SSL verification.




