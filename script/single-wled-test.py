
import socket
import time
import traceback
import sys
import requests
import json
import argparse
import logging


logging.basicConfig(filename='wled.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)



UDP_IP = "0.0.0.0"
UDP_PORT = 5252

wledToSensor = {
    '10.0.0.65': 'C8C9A3D1AFBC',
    '10.0.0.48': 'C8C9A3D1BCA8',
}


# def reverseKv(m):
#     d = {}
#     for k, v in m:
#         d[v] = k
#     return d

# sensorToWled = reverseKv(wledToSensor)


def control(ip, payload):
    url = f'http://{ip}/json/state'
    r = requests.post(url, json=payload)
    return r


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def switch(ip, state):
    payload = {'on': state, 'bri': 80, 'transition': 1, "seg":[{"col":[[0,255,200]]}]}
    control(ip, payload)


# flash target wled 5 times
def flash(ip):
    i = 0
    while i < 5:
        payload = {'on': True, 'bri': 80, 'transition': 1}
        control(ip, payload)
        time.sleep(0.2)
        payload = {'on': False, 'bri': 80, 'transition': 1}
        control(ip, payload)
        time.sleep(0.2)
        i += 1


SEEN = set()
DIST = []


def popOld():
    global DIST
    now = time.time()
    DIST = [d for d in DIST if now - d['ts'] < 0.2]

def addDist(dist):
    data = {'dist': dist, 'ts': time.time()}
    DIST.append(data)


def maybeSwitchLedOn():
    dists = [d['dist'] for d in DIST]
    currDist = DIST[-1]['dist']
    minDist = min(dists)
    onByDist = (currDist > 100 and currDist < 1200)
    distChange = abs(currDist - minDist)
    onByDistChange =  distChange > 100
    state = onByDist or onByDistChange

    if state:
        print(f'dist: {currDist} change: {distChange} OnByDist: {onByDist} OnByDistChange: {onByDistChange}')

    switch(ip, state)


def handleDistReq(req):
    mac = req['mac']
    if mac not in SEEN:
        SEEN.add(mac)
        logging.info(f'BIND {mac} {ip}')

    dist = req['dist']
    print(dist)
    if dist < 2000:
        addDist(dist)
        popOld()
        maybeSwitchLedOn()
    else:
        switch(ip, False) # invalid data what to do?




if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', "--ip", type=str, help='WLED ip address', required=True)
    ap.add_argument('-m', "--mac", type=str, help='Target proximity sensor mac address to test', required=True)
    args = vars(ap.parse_args())
    ip = args['ip']
    MAC = args['mac']
    while True:
        try:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            req = json.loads(data.decode('utf8'))
            if 'tpe' in req and req['tpe'] == 'dist' and req['mac'] == MAC:
                handleDistReq(req)
                continue

            logging.debug(f"IGNORE {req} FROM {addr}")
        except Exception as e:
            logging.error(f'Error {e}')
        finally:
            sent = sock.sendto(''.encode(), addr)
