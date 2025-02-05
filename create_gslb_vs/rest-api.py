#!/usr/bin/env python3

import requests
import json
import urllib.parse
import argparse
import getpass

# Disable SSL warnings 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to modify the SNAT pool of a virtual server
def modify_snat_pool(big_ip, vs_name, snat_pool, username, password):
    url = f"https://{big_ip}/mgmt/tm/ltm/virtual/~Common~{vs_name}"
    headers = {"Content-Type": "application/json"}
    data = {"sourceAddressTranslation": {"type": "snat", "pool": snat_pool}}
    
    response = requests.patch(url, headers=headers, data=json.dumps(data), auth=(username, password), verify=False)
    return response.status_code, response.text

# Function to add new pool members
def add_pool_member(big_ip, pool_name, member, username, password):
    url = f"https://{big_ip}/mgmt/tm/ltm/pool/~Common~{pool_name}/members"
    headers = {"Content-Type": "application/json"}
    data = {"name": member, "address": member.split(':')[0]}
    
    response = requests.post(url, headers=headers, data=json.dumps(data), auth=(username, password), verify=False)
    return response.status_code, response.text

# Function to disable current pool members
def disable_pool_member(big_ip, pool_name, member, username, password):
    encoded_member = urllib.parse.quote(member, safe='')
    url = f"https://{big_ip}/mgmt/tm/ltm/pool/~Common~{pool_name}/members/~Common~{encoded_member}"
    headers = {"Content-Type": "application/json"}
    data = {"session": "user-disabled"}
    
    response = requests.patch(url, headers=headers, data=json.dumps(data), auth=(username, password), verify=False)
    return response.status_code, response.text

# Main function
def main():
    parser = argparse.ArgumentParser(description='Script to modify SNAT pool and update pool members on an F5 BIG-IP device.')
    parser.add_argument('-b', '--big-ip', required=True, help='BIG-IP management IP address')
    parser.add_argument('-u', '--username', required=True, help='Username for BIG-IP authentication')
    
    args = parser.parse_args()
    
    big_ip = args.big_ip
    username = args.username
    password = getpass.getpass(prompt='Password: ')
    
    vs_name = input("Enter the virtual server name: ")
    snat_pool = input("Enter the SNAT pool name: ")
    pool_name = input("Enter the pool name associated with the Virtual Server: ")
    new_members_input = input("Enter new pool members (comma-separated list, e.g., 10.10.10.10:443,10.10.10.11:443): ")
    current_members_input = input("Enter current pool members to disable (comma-separated list, e.g., 10.100.100.10:443,10.100.100.100:443): ")
    
    new_members = new_members_input.split(',')
    current_members = current_members_input.split(',')
    
    # Modify SNAT pool
    status, response = modify_snat_pool(big_ip, vs_name, snat_pool, username, password)
    if status == 200:
        print("Modify SNAT Pool: Successful")
    else:
        print(f"Modify SNAT Pool Error: {status}, {response}")
    
    # Add new pool members
    for member in new_members:
        status, response = add_pool_member(big_ip, pool_name, member, username, password)
        if status == 200:
            print(f"Add Pool Member {member}: Successful")
        else:
            print(f"Add Pool Member {member} Error: {status}, {response}")
    
    # Disable current pool members
    for member in current_members:
        status, response = disable_pool_member(big_ip, pool_name, member, username, password)
        if status == 200:
            print(f"Disable Pool Member {member}: Successful")
        else:
            print(f"Disable Pool Member {member} Error: {status}, {response}")

if __name__ == "__main__":
    main()
