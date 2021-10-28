# WLED json doc:
# https://kno.wled.ge/interfaces/json-api/
#
# Data is valid if
# - the distance is smaller than P_DIST_MAX
# - or the current distance is less than P_DIST_MIN and time change from previous data point is larger than P_TS_MIN ms and previous distance is larger than P_DIST_MAX
# Person detected if
# - latest distance is valid and
# - latest distance is smaller than P_DIST_MAX


from concurrent.futures import ThreadPoolExecutor

import traceback
import socket
import time
import traceback
import sys
import requests
import json
import argparse
import logging


logging.basicConfig(filename='wled.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
executor = ThreadPoolExecutor(max_workers=10)


P_DIST_MAX = 1000
P_DIST_MIN = 120
P_TS_MIN = 1
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

def run_in_thread(func, *args):
    t = threading.Thread(target=func, args=args)
    t.start()

# overrides default config
configByIp = {
    '10.0.0.68': {
        'p_dist_min': 150,
        'p_ts_min' : 1.2,
        'debug': True,
    },
    '10.0.0.75': {
        'p_dist_min': 150,
        'p_ts_min' : 1.2,
    },
    '10.0.0.95': {
        'p_dist_min': 150,
    },
    '10.0.0.76': {
        'p_dist_min': 150,
    },    
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
    while len(xd) > 5:
        xd.pop(0)
    DIST[mac] = xd

def addDist(mac, dist):
    xd = DIST.get(mac, [])
    data = {'dist': dist, 'ts': time.time()}
    xd.append(data)
    DIST[mac] = xd

def getCurrentDistIfValid(mac):
    ip = sensorToWled[mac]
    debug = getConfigByIp(ip, 'debug', False)
    p_ts_min = getConfigByIp(ip, 'p_ts_min', P_TS_MIN)
    p_dist_max = getConfigByIp(ip, 'p_dist_max', P_DIST_MAX)
    p_dist_min = getConfigByIp(ip, 'p_dist_min', P_DIST_MIN)

    xd = DIST.get(mac, [])
    if len(xd) < 1:
        return None
    dist = xd[-1]['dist']

    if debug:
        logging.info(f'{ip} {mac} {dist}')

    if dist < p_dist_max and dist > p_dist_min:
        return dist

    if len(xd) < 2:
        return None

    tsChange = xd[-1]['ts'] - xd[-2]['ts']
    prevDist = xd[-2]['dist']

    if debug:
        logging.info(f'{ip} {mac} {dist} {tsChange}')

    if dist < P_DIST_MIN and tsChange > p_ts_min and prevDist < p_dist_max:
        return dist

    return None

def maybeSwitchLedOn(mac):
    ip = sensorToWled[mac]
    dist = getCurrentDistIfValid(mac)
    state = dist is not None

    debug = getConfigByIp(ip, 'debug', False)
    if state and debug:
        logging.info(f'{ip} {mac} {"ON" if state else "OFF"} {dist}')
    switch(ip, state)


def handleDistReq(req):
    mac = req['mac']
    dist = req['dist']
    ip = sensorToWled[mac]
    debug = getConfigByIp(ip, 'debug', False)

    if debug:
        logging.info(f'{ip} {mac} dist {dist}')

    addDist(mac, dist)
    popOld(mac)
    maybeSwitchLedOn(mac)

def reply(sock, addr):
    sock.sendto(''.encode(), addr)

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
                executor.submit(handleDistReq, req)
                continue

            logging.debug(f"IGNORE {req} FROM {addr}")
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            logging.exception('Main loop error')
        finally:
            executor.submit(reply, sock, addr)
