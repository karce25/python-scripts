#!/usr/bin/env python3

import requests
import urllib3
import argparse
import sys
import getpass
from requests.auth import HTTPBasicAuth

ARGS = None

def bigip_login():
    user = input("Username: ")
    password = getpass.getpass('Enter your password: ')
    return HTTPBasicAuth(user, password)

def get_virtual_servers(session, bigip, auth):
    url_vips = f"https://{bigip}/mgmt/tm/ltm/virtual?$select=name"
    response = session.get(url_vips, auth=auth, verify=False)
    response.raise_for_status()
    return response.json().get('items', [])

def get_virtual_server_details(session, bigip, vip_name, auth):
    url_vip_details = f"https://{bigip}/mgmt/tm/ltm/virtual/{vip_name}?expandSubcollections=true"
    response = session.get(url_vip_details, auth=auth, verify=False)
    response.raise_for_status()
    return response.json()

def main():
    global ARGS
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if sys.version_info < (3, 5):
        print('Please upgrade your Python version to 3.5 or higher')
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description='Retrieve Virtual Server configurations from BIG-IP')
    parser.add_argument('--bigip', type=str, required=True, help='BIG-IP address')
    parser.add_argument('--output_file', type=str, required=True, help='Output file to store the virtual server details')
    ARGS = parser.parse_args()
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    auth = bigip_login()
    
    virtual_servers = get_virtual_servers(session, ARGS.bigip, auth)
    
    print(f"Gathering information for {ARGS.bigip}, please wait...")
    
    with open(ARGS.output_file, 'w') as file:
        file.write("Virtual Server Name, Virtual Server IP, Virtual Server Port, Has HTTP Profile, HTTP Profile Name, Has Client SSL Profile, Client SSL Profile Name\n")
        for vip in virtual_servers:
            vip_details = get_virtual_server_details(session, ARGS.bigip, vip['name'], auth)
            vip_name = vip_details.get('name', 'N/A')
            destination = vip_details.get('destination', 'N/A')
            ip, port = 'N/A', 'N/A'
            if destination != 'N/A':
                ip_port = destination.split('/')[-1]
                ip, port = ip_port.split(':')
            profiles = vip_details.get('profilesReference', {}).get('items', [])
            has_http_profile = False
            http_profile_name = 'N/A'
            has_client_ssl_profile = False
            client_ssl_profile_name = 'N/A'
            
            for profile in profiles:
                if profile['context'] == 'all' and 'profile/http' in profile.get('nameReference', {}).get('link', ''):
                    has_http_profile = True
                    http_profile_name = profile['name']
                if profile['context'] == 'clientside' and 'profile/client-ssl' in profile.get('nameReference', {}).get('link', ''):
                    has_client_ssl_profile = True
                    client_ssl_profile_name = profile['name']
            
            file.write(f"{vip_name}, {ip}, {port}, {has_http_profile}, {http_profile_name}, {has_client_ssl_profile}, {client_ssl_profile_name}\n")
        print(f"Virtual server details have been written to {ARGS.output_file}")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()
