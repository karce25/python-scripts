#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth
import csv
import argparse
import urllib3


#Disable insecure warnings generated by the request 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Endpoint to gather the virtual address, using verify false to disable SSL cert verification

def send_get_request(ip_address, endpoint, username, password):
    url = f"https://{ip_address}/{endpoint}"
    response = requests.get(url, auth=HTTPBasicAuth (username, password), verify=False)
    
    return response.json()


# Argument parser to accept command-line arguments
parser = argparse.ArgumentParser(description="Extract virtual addresses from multiple BIG-IPs and save to a CSV file.")
parser.add_argument('-file', type=str, required=True, help='Path to the CSV file containing the BIG-IP IP addresses.')

args = parser.parse_args()
csv_file_path = args.file

# Reads the csv file with the managament ip addresses of the BIG-IP or host 

big_ip_ips = []
with open(csv_file_path, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  
    for row in csvreader:
        big_ip_ips.append(row[0])
        
#Credentials assuming the same user is configured on the BIG-IPs     
username = 'admin'
password = 'admin'
endpoint = '/mgmt/tm/ltm/virtual-address?%24select=address'

# File to store virtual addresses
output_file = 'all_virtual_addresses.csv'
        

# Process each BIG-IP

with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['BIG-IP MGMT', 'Virtual Address'])  # Write the header of the csv file

    for ip_address in big_ip_ips:
        response_json = send_get_request(ip_address, endpoint, username, password)
        if response_json and "items" in response_json:
            for item in response_json["items"]:
                if "address" in item:
                    csvwriter.writerow([ip_address, item["address"]])  # Write each virtual address with corresponding BIG-IP mgmt IP or hostname
            print(f"Virtual addresses from {ip_address} have been written to '{output_file}'.")
        else:
            print(f"No virtual addresses found in the response from {ip_address}.")


for pool in $(tmsh list gtm wideip a test.com pools | awk '/^ {8}[a-zA-Z0-9_.-]+ {$/ {print $1}'); do tmsh list gtm pool a $pool members; done
