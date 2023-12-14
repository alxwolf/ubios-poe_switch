import argparse
import json
import logging
import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Change the PoE Mode of UniFi switches controlled by a UDM (Pro).')
parser.add_argument("controller", help="hostname or IP address of UniFi Controller")
parser.add_argument("username", help="username with admin rights on UniFi Controller")
parser.add_argument("password", help="corresponding password for admin user")
parser.add_argument("mac", help="MAC address (with or without colons) of switch")
parser.add_argument("ports", help="port numbers to acquire new state (list separated by comma, e.g., '5,6,7'")
parser.add_argument("state", help="desired state of PoE ports, e.g., 'auto' or 'off'")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args=parser.parse_args()

# parameters
base_url = 'https://%s' % args.controller
login_endpoint = base_url + '/api/auth/login'
logout_endpoint = base_url + '/api/auth/logout'

login_data = {
    'username': args.username,
    'password': args.password
}

get_device_settings_endpoint = base_url + '/proxy/network/api/s/default/stat/device/%s' % args.mac
set_device_settings_endpoint = base_url + '/proxy/network/api/s/default/rest/device/'
ports_array = args.ports.split(',')
desired_poe_state = args.state

if (args.verbose):
    loglevel=logging.DEBUG
else:
    loglevel=logging.INFO

logging.basicConfig(level=loglevel, format='%(asctime)s - %(levelname)s - %(message)s')

#
# Logout - this requires the X-CSRF-Token
#

def logout():
    logging.info("Logging out via %s.", logout_endpoint)
    # UniFi OS versions before 3.2.7
    logout = s.post(logout_endpoint, headers = {'x-csrf-token': login.headers['X-CSRF-Token']}, verify = False, timeout = 1)
    # Unifi OS versions from 3.2.7
    # logout = s.post(logout_endpoint, headers = {'x-csrf-token': login.headers['X-Csrf-Token']}, verify = False, timeout = 1)
    
    if (logout.status_code == 200):
        logging.debug("Success.")
        sys.exit()
    else:
        logging.debug("Failed with return code %s", logout)
        sys.exit()


# Login and get auth token from Cookies plus X-CSRF-Token from header
# 
# working call with cURL:  Login:
# curl -X POST --data 'username=user&password=pass' -c cookie.txt https://udm/api/auth/login
# Get status:
# curl -X GET -b cookie.txt https://udm/proxy/network/api/s/default/stat/device/abcdef012
# 

logging.info("Trying to login to %s with data %s", login_endpoint, str(login_data))

s = requests.Session()

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8"
}

login = s.post(login_endpoint, headers = headers,  json = login_data , verify = False, timeout = 1)

if (login.status_code == 200):
    cookies = login.cookies
    logging.debug("Success. Cookies received:")
    for c in cookies:
        logging.debug("%s ==> %s", c.name, c.value)
    # UniFi OS versions before 3.2.7
    logging.debug("X-CSRF-Token: %s", login.headers['X-CSRF-Token'])
    # UniFi OS versions from 3.2.7
    # logging.debug("X-CSRF-Token: %s", login.headers['X-Csrf-Token'])

else:
    logging.debug("Login failed with return code %s", login.status_code)
    sys.exit()

# Get current port_overrides config for device
logging.info ("Read current settings from %s", get_device_settings_endpoint)

r = s.get(get_device_settings_endpoint, headers = headers, verify = False, timeout = 1)

if (r.status_code == 200):
    logging.debug("Success.")
else:
    logging.debug("Failed with return code %s", r)
    logout()

device_json = r.json()
port_overrides = device_json['data'][0]['port_overrides']
device_id = device_json['data'][0]['device_id']

set_device_settings_endpoint = set_device_settings_endpoint + device_id

# Update the port_overrides config with new settings
for x in ports_array:
    for value in port_overrides:
        if value['port_idx'] == int(x):
            if 'poe_mode' in value:
                if (value['poe_mode'] != desired_poe_state):
                    logging.info("Updating port_idx %s from %s to %s", value['port_idx'], value['poe_mode'], desired_poe_state)
                    value['poe_mode'] = desired_poe_state
                else:
                    logging.info("port_idx %s already set to %s", value['port_idx'], desired_poe_state)


# Set the updated port_overides config for device
new_port_overrides = { 'port_overrides': port_overrides }

logging.info("Trying to update port overrides on %s", set_device_settings_endpoint)

logging.debug("%s", json.dumps(new_port_overrides))

# UniFi OS versions before 3.2.7
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "x-csrf-token": login.headers['X-CSRF-Token']
}

# UniFi OS versions from 3.2.7
#headers = {
#    "Accept": "application/json",
#    "Content-Type": "application/json; charset=utf-8",
#    "x-csrf-token": login.headers['X-Csrf-Token']
#}

update = s.put(set_device_settings_endpoint, headers = headers, data = json.dumps(new_port_overrides), verify = False, timeout = 1)

if (update.status_code == 200):
    logging.debug("Success.")
else:
    logging.debug("Failed with return code %s", update.status_code)

logout()
