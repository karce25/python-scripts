import requests
import json

# Replace these variables with your actual BIG-IP credentials and IP
BIGIP_IP = 'ip_address'
BIGIP_USERNAME = 'user'
BIGIP_PASSWORD = 'passowrd'

# Replace with actual server name and virtual server details
SERVER_NAME = 'server_name'
VIRTUAL_SERVER_NAME = 'Virtual_server_name'
VIRTUAL_SERVER_IP = '10.10.10.10'
VIRTUAL_SERVER_PORT = 80
POOL_NAME = 'pool_name'
WIDE_IP_NAME = 'test.com'

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_virtual_servers():
    url = f'https://{BIGIP_IP}/mgmt/tm/gtm/server/{SERVER_NAME}'
    response = requests.get(url, auth=(BIGIP_USERNAME, BIGIP_PASSWORD), verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve virtual servers. Status code: {response.status_code}, Response: {response.text}")
        return None

def create_virtual_server():
    url = f'https://{BIGIP_IP}/mgmt/tm/gtm/server/{SERVER_NAME}/virtual-servers'
    headers = {'Content-Type': 'application/json'}
    data = {
        "name": VIRTUAL_SERVER_NAME,
        "destination": f"{VIRTUAL_SERVER_IP}:{VIRTUAL_SERVER_PORT}"
    }
    response = requests.post(url, auth=(BIGIP_USERNAME, BIGIP_PASSWORD), headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200 or response.status_code == 201:
        return True
    else:
        print(f"Failed to create virtual server {VIRTUAL_SERVER_NAME}. Status code: {response.status_code}, Response: {response.text}")
        return False

def create_pool():
    url = f'https://{BIGIP_IP}/mgmt/tm/gtm/pool/a'
    headers = {'Content-Type': 'application/json'}
    data = {
        "name": POOL_NAME,
        "loadBalancingMode": "round-robin",
        "members": [{
            "name": f"{SERVER_NAME}:{VIRTUAL_SERVER_NAME}"
        }]
    }
    response = requests.post(url, auth=(BIGIP_USERNAME, BIGIP_PASSWORD), headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200 or response.status_code == 201:
        return True
    else:
        print(f"Failed to create pool {POOL_NAME}. Status code: {response.status_code}, Response: {response.text}")
        return False

def create_wide_ip():
    url = f'https://{BIGIP_IP}/mgmt/tm/gtm/wideip/a'
    headers = {'Content-Type': 'application/json'}
    data = {
        "name": WIDE_IP_NAME,
        "pools": [{
            "name": POOL_NAME
        }]
    }
    response = requests.post(url, auth=(BIGIP_USERNAME, BIGIP_PASSWORD), headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200 or response.status_code == 201:
        return True
    else:
        print(f"Failed to create wide-IP {WIDE_IP_NAME}. Status code: {response.status_code}, Response: {response.text}")
        return False

def main():
    virtual_servers = get_virtual_servers()
    
    if virtual_servers:
        virtual_server_exists = any(vs['name'] == VIRTUAL_SERVER_NAME for vs in virtual_servers.get('virtual-servers', []))

        if not virtual_server_exists:
            print(f"Virtual server {VIRTUAL_SERVER_NAME} does not exist. Creating...")
            if create_virtual_server():
                print(f"Virtual server {VIRTUAL_SERVER_NAME} created successfully.")
                print(f"Creating pool {POOL_NAME}...")
                if create_pool():
                    print(f"Pool {POOL_NAME} created successfully.")
                    print(f"Creating wide-IP {WIDE_IP_NAME}...")
                    if create_wide_ip():
                        print(f"Wide-IP {WIDE_IP_NAME} created successfully.")
                    else:
                        print(f"Failed to create wide-IP {WIDE_IP_NAME}.")
                else:
                    print(f"Failed to create pool {POOL_NAME}.")
            else:
                print(f"Failed to create virtual server {VIRTUAL_SERVER_NAME}.")
        else:
            print(f"Virtual server {VIRTUAL_SERVER_NAME} already exists.")
    else:
        print("Failed to retrieve virtual servers.")

if __name__ == '__main__':
    main()
