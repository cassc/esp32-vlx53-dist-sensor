# Gen qrcode for labeling using jingchen labeling machine
#
# Usage:
# Auto read from connected device
# python3 gen-qrcode.py --auto
#
# Manually specify mac address
# python3 gen-qrcode.py --left  98F4AB6BD460 --right  98F4AB6BD460

import os
import qrcode
import argparse
from PIL import Image, ImageFont, ImageDraw

import subprocess
from subprocess import check_output

scale = 3.7795275591

height = 240
width = 360

ap = argparse.ArgumentParser()
ap.add_argument("--left", help="MAC address on left", type=str, required=False)
ap.add_argument("--right", help="MAC address on right", type=str, required=False)
ap.add_argument("--auto", help="Read MAC address from UART", action='store_true')
args = vars(ap.parse_args())

def read_mac():
    cmd = 'esptool.py read_mac'.split()
    r = check_output(cmd)
    lines = r.decode().split('\n')
    for line in lines:
        if line.startswith('MAC: '):
            return line[5:].replace(':', '').upper()
    return ''

def gen_qr(mac):
    qr = qrcode.make(mac)
    qr = qr.resize((120, 120))
    return qr


left = args['left']
right = args['right']
if args['auto']:
    mac = read_mac()
    left = mac
    right = mac



qrl = gen_qr(left)
qrr = gen_qr(right)
font = ImageFont.truetype('/usr/share/fonts/droid/DroidSansMono.ttf', 28)

im = Image.new(mode="RGB", size=(width, height), color=(255,255,255,0))
im.paste(qrl, (5, 0))
im.paste(qrr, (5, 120))
draw = ImageDraw.Draw(im)
draw.text((120, 40), left, (0, 0, 0), font=font, direction='rtl')
draw.text((120, 170), right, (0, 0, 0), font=font, direction='rtl')

im = im.resize((int(width*scale), int(height*scale)))
im = im.rotate(90, expand=True)
im.save(f'qr-{left}-{right}.jpg')
