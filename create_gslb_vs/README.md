# BIG-IP GSLB Virtual Server, Pool, and Wide-IP Creation Script

## Overview
This Python script allows you to add a GSLB virtual server into an existing server, checks if the virtual server exists, and if it does not exist create a pool, and wide-IP on a BIG-IP GTM system using REST API calls.

## Prerequisites

- ``` requests ``` library
- ``` json ``` library
- ``` argparse ``` library

## Usage

The script accepts the following command-line arguments:

``` -b, --bigip-ip: ``` BIG-IP IP address (required)
``` -u, --username: ``` BIG-IP username (required)
``` -p, --password: ``` BIG-IP password (required)

Interactive Prompts
The script will prompt you for the following information:

Server name
Virtual server name
Virtual server IP
Virtual server port (integer)
Wide-IP name

# Running the script

python add_servers.py -b <BIG-IP_IP> -u <USERNAME> -p <PASSWORD>

# Output

The script generates a CSV file named all_virtual_addresses.csv in the same directory as the script. This file contains the virtual addresses extracted from each BIG-IP device

# Example output

$ python add_vs_gslb.py -b 10.10.10.10 -u admin -p admin

Enter the server name: testserver
Enter the virtual server name: vs_test
Enter the virtual server IP: 10.10.10.10
Enter the virtual server port: 443
Enter the wide-IP name: example-wide-ip

Virtual server testserver does not exist. Creating...
Virtual server testserver created successfully.
Creating pool testserver...
Pool testserver created successfully.
Creating wide-IP example-wide-ip...
Wide-IP example-wide-ip created successfully.



# Notes

- Security Warning: The script uses verify=False to disable SSL verification.





