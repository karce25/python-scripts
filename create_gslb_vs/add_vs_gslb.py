#!/usr/bin/env python3

import requests
import json
import argparse

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_virtual_servers(bigip_ip, bigip_username, bigip_password, server_name):
    url = f'https://{bigip_ip}/mgmt/tm/gtm/server/{server_name}'
    response = requests.get(url, auth=(bigip_username, bigip_password), verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve virtual servers. Status code: {response.status_code}, Response: {response.text}")
        return None

def create_virtual_server(bigip_ip, bigip_username, bigip_password, server_name, virtual_server_name, virtual_server_ip, virtual_server_port):
    url = f'https://{bigip_ip}/mgmt/tm/gtm/server/{server_name}/virtual-servers'
    headers = {'Content-Type': 'application/json'}
    data = {
        "name": virtual_server_name,
        "destination": f"{virtual_server_ip}:{virtual_server_port}"
    }
    response = requests.post(url, auth=(bigip_username, bigip_password), headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200 or response.status_code == 201:
        return True
    else:
        print(f"Failed to create virtual server {virtual_server_name}. Status code: {response.status_code}, Response: {response.text}")
        return False

def create_pool(bigip_ip, bigip_username, bigip_password, pool_name, server_name, virtual_server_name):
    url = f'https://{bigip_ip}/mgmt/tm/gtm/pool/a'
    headers = {'Content-Type': 'application/json'}
    data = {
        "name": pool_name,
        "loadBalancingMode": "round-robin",
        "members": [{
            "name": f"{server_name}:{virtual_server_name}"
        }]
    }
    response = requests.post(url, auth=(bigip_username, bigip_password), headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200 or response.status_code == 201:
        return True
    else:
        print(f"Failed to create pool {pool_name}. Status code: {response.status_code}, Response: {response.text}")
        return False

def create_wide_ip(bigip_ip, bigip_username, bigip_password, wide_ip_name, pool_name):
    url = f'https://{bigip_ip}/mgmt/tm/gtm/wideip/a'
    headers = {'Content-Type': 'application/json'}
    data = {
        "name": wide_ip_name,
        "pools": [{
            "name": pool_name
        }]
    }
    response = requests.post(url, auth=(bigip_username, bigip_password), headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200 or response.status_code == 201:
        return True
    else:
        print(f"Failed to create wide-IP {wide_ip_name}. Status code: {response.status_code}, Response: {response.text}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create virtual server, pool, and wide-IP on BIG-IP GTM.')
    parser.add_argument('-b', '--bigip-ip', required=True, help='BIG-IP IP address')
    parser.add_argument('-u', '--username', required=True, help='BIG-IP username')
    parser.add_argument('-p', '--password', required=True, help='BIG-IP password')
    
    args = parser.parse_args()
    
    bigip_ip = args.bigip_ip
    bigip_username = args.username
    bigip_password = args.password
    
    server_name = input("Enter the server name: ")
    virtual_server_name = input("Enter the virtual server name: ")
    virtual_server_ip = input("Enter the virtual server IP: ")
    virtual_server_port = int(input("Enter the virtual server port: "))
    pool_name = input("Enter the pool name: ")
    wide_ip_name = input("Enter the wide-IP name: ")

    virtual_servers = get_virtual_servers(bigip_ip, bigip_username, bigip_password, server_name)
    
    if virtual_servers:
        virtual_server_exists = any(vs['name'] == virtual_server_name for vs in virtual_servers.get('virtual-servers', []))

        if not virtual_server_exists:
            print(f"Virtual server {virtual_server_name} does not exist. Creating...")
            if create_virtual_server(bigip_ip, bigip_username, bigip_password, server_name, virtual_server_name, virtual_server_ip, virtual_server_port):
                print(f"Virtual server {virtual_server_name} created successfully.")
                print(f"Creating pool {pool_name}...")
                if create_pool(bigip_ip, bigip_username, bigip_password, pool_name, server_name, virtual_server_name):
                    print(f"Pool {pool_name} created successfully.")
                    print(f"Creating wide-IP {wide_ip_name}...")
                    if create_wide_ip(bigip_ip, bigip_username, bigip_password, wide_ip_name, pool_name):
                        print(f"Wide-IP {wide_ip_name} created successfully.")
                    else:
                        print(f"Failed to create wide-IP {wide_ip_name}.")
                else:
                    print(f"Failed to create pool {pool_name}.")
            else:
                print(f"Failed to create virtual server {virtual_server_name}.")
        else:
            print(f"Virtual server {virtual_server_name} already exists.")
    else:
        print("Failed to retrieve virtual servers.")

if __name__ == '__main__':
    main()
