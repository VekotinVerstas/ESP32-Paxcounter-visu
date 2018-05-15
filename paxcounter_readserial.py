# coding=utf-8

import serial
import struct, sys
import sys
import datetime
import time
import re
import pytz
import json

baudrate = 115200
MAX_AGE = 60

def parse_line(line):
    """
    [I][macsniff.cpp:75] mac_add(): known BLTH RSSI -62dBi -> MAC 0665D2BD -> Hash 2FC8 -> WiFi:17  BLTH:2 -> 79404 Bytes left
    [I][macsniff.cpp:75] mac_add(): known WiFi RSSI -79dBi -> MAC 29F1233B -> Hash FB99 -> WiFi:17  BLTH:2 -> 79396 Bytes left
    """
    x = line.split()
    data = {
        'seen': x[2],
        'type': x[3],
        'rssi': re.sub("\D", "", x[5]),
        'mac': x[8],
    }
    return data


ser = serial.Serial()
ser.port = sys.argv[1]
ser.baudrate = baudrate
ser.open()
ser.flushInput()

wifis = {}
bles = {}
last_cleanup = time.time()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_now():
    return pytz.UTC.localize(datetime.datetime.utcnow())


def get_age(ts):
    age = (get_now() - ts).total_seconds()
    return age


while True:
    line = ser.readline().decode("utf-8").strip()
    #    line = str(line)
    #    line = line.strip()
    ts = get_now()
    if line.find('mac_add') > 0:
        data = parse_line(line)
        if data['type'].lower() == 'wifi':
            mac = data['mac']
            hit = (ts, data['rssi'])
            if mac not in wifis:
                wifis[mac] = data
                wifis[mac].pop('seen')
                wifis[mac].pop('type')
                wifis[mac]['hits'] = [hit, ]
                wifis[mac]['count'] = 1
            else:
                wifis[mac]['count'] += 1
                if get_age(wifis[mac]['hits'][-1][0]) >= 1.0:
                    wifis[mac]['hits'].append(hit)
        # print(wifis)
    if time.time() - last_cleanup > 5:
        to_remove = []
        for k, v in wifis.items():
            age = get_age(v['hits'][-1][0])
            if age > MAX_AGE:
                print('GONE: {} {:6.2f} {:3d}'.format(k, age, v['count']))
                to_remove.append(k)
            else:
                print('HERE: {} {:6.2f} {:3d}'.format(k, age, v['count']))
        print()
        with open('wifilog.txt', 'at') as f:
            for k in to_remove:
                r = wifis.pop(k)
                r_json = json.dumps(r, default=json_serial)
                f.write(r_json + '\n')
                # print(json.dumps(r, indent=1, default=json_serial))
        last_cleanup = time.time()
