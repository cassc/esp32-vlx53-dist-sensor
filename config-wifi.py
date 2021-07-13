# Not working, DONOT use
# Flash WT32 Eth01 with static IP configuration
# Usage:
# Configure WiFi with dynamic IP:
# python3 config-wifi.py --ssid playscape --password makeplayscape
# Configure WiFi with static IP:
# python3 config-wifi.py --ssid MAKE --password wemakedigital --ip 10.0.2.110 --gateway 10.0.2.1 --subnet 255.255.255.0


import argparse
import os
import sys
import requests
import time
import subprocess
from subprocess import check_output


AP_IP = '172.217.28.1'

ap = argparse.ArgumentParser()
ap.add_argument("--target", help="ESP target IP", type=str, required=False, default=AP_IP)
ap.add_argument("--ssid", help="WiFi ssid", type=str, required=True)
ap.add_argument("--password", help="WiFi password", type=str, required=True)
ap.add_argument("--ip", help="Static IP address", type=str, default='', required=False)
ap.add_argument("--gateway", help="Gateway address", type=str, required=False)
ap.add_argument("--subnet", help="Subnet mask address", type=str, required=False)
ap.add_argument("--dns", help="DNS 1", type=str, required=False)

args = vars(ap.parse_args())

ssid = args['ssid']
target = args['target']
password = args['password']
ip = args['ip']
gateway = args['gateway']
subnet = args['subnet']
dns = args['dns']

data = dict(SSID=ssid, Passphrase=password)
data['apply'] = 'Apply'
if len(ip) > 0:
    data['sip'] = ip
    data['gw'] = gateway
    data['nm'] = subnet
    data['ns1'] = dns
else:
    data['dhcp'] = 'en'

# data = f"SSID={ssid}&Passphrase={password}&dhcp=en&apply=Apply"
# if len(ip) > 0:
#     data = f"SSID={ssid}&Passphrase={password}&sip={ip}&gw={gateway}&nm={subnet}&apply=Apply"
# data = f"SSID={ssid}&Passphrase={password}&sip={ip}&gw={gateway}&nm={subnet}&ns1=10.0.2.1&apply=Apply"
print(data)


if target == AP_IP:
    cmd_conn_ap = 'nmcli d wifi connect make_tof password 12345678'.split()
    success = False
    while not success:
        os.system('nmcli device wifi rescan')
        try:
            check_output(cmd_conn_ap)
            success = True
        except subprocess.CalledProcessError as e:
            pass
        finally:
            time.sleep(1)

    if not success:
        sys.exit(1)

url = f'http://{target}/_ac/connect'
print(f'Sending request to {url}')

# headers={'Content-Type': 'application/x-www-form-urlencoded'}
# r = requests.post(url, headers=headers, data=data)
r = requests.post(url, data=data)


print(f'Set ip returns {r}')


def read_mac():
    cmd = 'esptool.py read_mac'.split()
    r = check_output(cmd)
    lines = r.decode().split('\n')
    for line in lines:
        if line.startswith('MAC: '):
            return line[5:].replace(':', '').upper()
    return ''


print(f'Config success for {read_mac()}')
