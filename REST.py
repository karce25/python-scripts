import requests
from requests.auth import HTTPBasicAuth

def send_get_request(ip_address, endpoint, username, password):
    url = f"https://{ip_address}/{endpoint}"
    response = requests.get(url, auth=HTTPBasicAuth (username, password), verify=False)
    
    return response.json()

# Example usage
ip_address = 'x.x.x.x'  #Replace with correct IP address
endpoint = '/mgmt/tm/shared/licensing/registration'  #endpoint to query
username = 'username'
password = 'password'

def extract_value (response_json, key):
    for k, v in response_json.items():
        if k==key:
            return v
        elif isinstance (v, dict):
            result = extract_value (v,key)
            if result:
                return result
    return None

response_json = send_get_request(ip_address, endpoint, username, password)
registrationKey= extract_value (response_json, 'registrationKey')
print (registrationKey, ip_address)