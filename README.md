# Virtual Address Extractor from BIG-IP Devices

## Overview
This script extracts virtual addresses from multiple BIG-IP devices and saves the results into a CSV file. It reads the BIG-IP IP addresses from a specified CSV file and uses common credentials and a single endpoint to send requests to each BIG-IP device

## Prerequisites

- ``` requests ``` library
- A CSV file containing the IP addresses or hostnames of the BIG-IP devices
- Sets common credentials (username and password)

## Usage

Create a CSV file with the following format (could be either hostname or IP address) :

```
ip_address
10.10.10.10
10.10.10.11

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




