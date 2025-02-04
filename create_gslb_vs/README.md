# BIG-IP GSLB Virtual Server, Pool, and Wide-IP Creation Script

## Overview
This Python script allows you to add a GSLB virtual server into an existing server, checks if the virtual server exists, and if it does not exist create a pool, and wide-IP on a BIG-IP GTM system using REST API calls.

## Prerequisites

- ``` requests ``` library
- ``` json ``` library
- ``` argparse ``` library

## Usage

The script accepts the following command-line arguments:

- ``` -b, --bigip-ip: ``` BIG-IP IP address (required)
- ``` -u, --username: ``` BIG-IP username (required)
- ``` -p, --password: ``` BIG-IP password (required)

Interactive Prompts
The script will prompt you for the following information:

- Server name
- Virtual server name
- Virtual server IP
- Virtual server port (integer)
- Wide-IP name

# Running the script

``` #./add_vs_gslb.py -b <BIG-IP_IP> -u <USERNAME> -p <PASSWORD> ``` 

# Output

The script generates a CSV file named all_virtual_addresses.csv in the same directory as the script. This file contains the virtual addresses extracted from each BIG-IP device

# Example output

#./add_vs_gslb.py -b 10.10.10.10 -u admin -p admin

``` 
Enter BIG-IP password: 
Enter the server name: server_test
Enter the virtual server name: virtual_test
Enter the virtual server IP: 10.10.10.10
Enter the virtual server port: 443
Enter the pool name: test_pool
Enter the wide-IP name: mywideip.com
Virtual server virtual_test does not exist. Creating...
Virtual server virtual_test created successfully.
Creating pool test_pool ...
Pool test_pool created successfully.
Creating wide-IP mywideip.com...
Wide-IP mywideip.com created successfully.

```
# Error Handling

If an error occurs during any of the API calls, the script will print a detailed error message, including the status code and response from the server.

Example:

``` 
Failed to create virtual server test_virtual. Status code: 400, Response: {"code":400,"message":"01070224:3: Pool Member on Pool /Common/test_pool of type A must contain a valid Virtual Server name because it is a terminal member.","errorStack":[],"apiError":3}

```

# Notes

- Security Warning: The script uses verify=False to disable SSL verification.






