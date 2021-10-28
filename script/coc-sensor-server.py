# WLED json doc:
# https://kno.wled.ge/interfaces/json-api/

import traceback
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
    '10.0.0.65':'C8C9A3D1B9FC',
    '10.0.0.48':'C8C9A3D1BCA8',
    '10.0.0.67':'C8C9A3D1C030',
    '10.0.0.49':'C8C9A3D1B800',
    '10.0.0.97':'C8C9A3D1C370',
    '10.0.0.69':'C8C9A3D1BCAC',
    '10.0.0.95':'C8C9A3D1B9F8',
    '10.0.0.68':'C8C9A3D1BE2C',
    '10.0.0.79':'C8C9A3D1B298',
    '10.0.0.47':'C8C9A3D1B940',
    '10.0.0.98':'C8C9A3D1AD98',
    '10.0.0.35':'C8C9A3D1C188',
    '10.0.0.37':'C8C9A3D1B53C',
    '10.0.0.45':'C8C9A3D1C1BC',
    '10.0.0.46':'C8C9A3D1BDE0',
    '10.0.0.38':'C8C9A3D1BF64',
    '10.0.0.36':'C8C9A3D1AD20',
    '10.0.0.96':'C8C9A3D1C0BC',
    '10.0.0.77':'C8C9A3D1AF40',
    '10.0.0.67':'C8C9A3D1C030',
    '10.0.0.75':'C8C9A3D1C37C',
    '10.0.0.76':'C8C9A3D1AFBC',
    '10.0.0.78':'C8C9A3D1C1D0',
    '10.0.0.66':'C8C9A3D1B958',
    '10.0.0.39':'C8C9A3D1AF98',

}


# overrides default config
configByIp = {
    '10.0.0.68': {
        # mininum history distance, smaller value produces higher noise
        'minDist': 100,
        # increase this to reduce noise
        'minHistDataCount': 8,
        # enable debugging for this sensor
        # 'debug': True,
    },
    '10.0.0.75': {
        'minDist': 100,
        'minHistDataCount': 5,
    },
    '10.0.0.69': {
        'minHistDataCount': 5,
    },
    '10.0.0.78': {
        'minDist': 100,
        'minHistDataCount': 5,
    }
}

def getConfigByIp(ip, key, default=None):
    config = configByIp.get(ip)
    return config.get(key, default) if config is not None else default


wledStates = {}


def reverseKv(m):
    d = {}
    for _, (k, v) in enumerate(m.items()):
        d[v] = k
    return d

sensorToWled = reverseKv(wledToSensor)


def control(ip, payload):
    url = f'http://{ip}/json/state'
    r = requests.post(url, json=payload, timeout=(0.5, 0.5))
    success = r.status_code == 200
    if not success:
        logging.warn(f'Control error: {url} {r}')
    return success


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def switch(ip, state):
    prevState = wledStates.get(ip, None)

    # check state to avoid sending too many requests
    if prevState is None or prevState != state:
        # transition value will be n * 100 ms
        transition = 2 if state else 5
        payload = {'on': state, 'bri': 80, 'transition': transition, "seg":[{"col":[[0,255,200]]}]}
        if control(ip, payload):
            wledStates[ip] = state

def makeUdpPacket(numLeds, r, g, b):
    # https://kno.wled.ge/interfaces/udp-realtime/
    proto = 4 # DNRGB
    timeout = 255
    offset = [0, 0]
    data = [proto, timeout] + offset
    for i in range(numLeds):
        data.append(r)
        data.append(g)
        data.append(b)
    return bytearray(data)

def switchByUDP(ip, state):
    port = 21324

    clientSock = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    color = [100, 100, 100] if state else [0, 0, 0]
    pack = makeUdpPacket(151, *color)
    clientSock.sendto (pack, (ip, port))


DIST = {}

def popOld(mac):
    xd = DIST.get(mac, [])
    ip = sensorToWled[mac]
    histDuration = getConfigByIp(ip, 'histDuration', 0.2)
    now = time.time()
    xd = [d for d in xd if now - d['ts'] < histDuration]
    DIST[mac] = xd

def addDist(mac, dist):
    xd = DIST.get(mac, [])
    data = {'dist': dist, 'ts': time.time()}
    xd.append(data)
    DIST[mac] = xd


def maybeSwitchLedOn(mac):
    ip = sensorToWled[mac]
    xd = DIST.get(mac, [])
    dists = [d['dist'] for d in xd]
    currDist = xd[-1]['dist']
    minDist = min(dists)
    maxDist = max(dists)
    # for person standing in range
    onByDist = (currDist > 200 and currDist < 1000)
    # for person standing still close
    minHistDataCount = getConfigByIp(ip, 'minHistDataCount', 2)
    debug = getConfigByIp(ip, 'debug', False)
    hasMinDataCount = len(dists) > minHistDataCount
    onBySmallDist = minDist > getConfigByIp(ip, 'minDist', 80) and maxDist < 1000 and hasMinDataCount
    distChange = abs(currDist - minDist)
    # for person passing by
    onByDistChange =  distChange > 100
    state = onByDist or onByDistChange or onBySmallDist

    if state or debug:
        logging.info(f'{ip} {"ON" if state else "OFF"} dist: {currDist} change: {distChange} ({minDist}, {maxDist}) OnByDist: {onByDist} OnByDistChange: {onByDistChange} onBySmallDist: {onBySmallDist}')

    switch(ip, state)


def handleDistReq(req):
    mac = req['mac']
    dist = req['dist']
    ip = sensorToWled[mac]
    debug = getConfigByIp(ip, 'debug', False)
    valid = dist < 2000

    if debug:
        logging.info(f'{ip} DIST {"VALID" if valid else "INVALID"} {dist}')

    if valid:
        # print(f'{mac} {dist}')
        addDist(mac, dist)
        popOld(mac)
        maybeSwitchLedOn(mac)
    else:
        # clear history data if got invalid reading
        DIST[mac] = []
        switch(ip, False)




if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    args = vars(ap.parse_args())
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = data.decode('utf8')
            try:
                req = json.loads(msg)
            except Exception:
                logging.warning(f'Decode json failed: {msg}')
                continue
            if 'tpe' in req and req['tpe'] == 'dist' and req['mac'] in sensorToWled:
                handleDistReq(req)
                continue

            logging.debug(f"IGNORE {req} FROM {addr}")
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logging.exception('Main loop error')
        finally:
            sent = sock.sendto(''.encode(), addr)
