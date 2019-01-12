"""
Read Paxcounter debug data from serial port and write it to a file
after some calculations.

TODO: cleanup and reorganise
TODO: add argparse and --quiet / --verbose etc switches.
"""
import serial
import struct, sys
import sys
import datetime
import time
import re
import pytz
import json
import re
import argparse

baudrate = 115200  # TODO: to args
MAX_AGE = 10  # TODO: to args

P = re.compile(' (new|known) +(WiFi|BLTH) +RSSI +(-[\d]+)dBi.*MAC ([\d\w]{8,12}) ')


def parse_line(line):
    """
    [I][macsniff.cpp:124] mac_add(): known WiFi RSSI -73dBi -> MAC 98B3E5FB -> Hash 36A0 -> WiFi:10  BLTH:13 -> 50980 Bytes left
    [I][macsniff.cpp:124] mac_add(): known BLTH RSSI -81dBi -> MAC 36FC8190 -> Hash 6720 -> WiFi:10  BLTH:13 -> 51160 Bytes left
    [I][macsniff.cpp:130] mac_add(): known BLTH RSSI -81dBi -> MAC D86ABF895CF4 -> Hash 8C27 -> WiFi:8  BLTH:9 -> 51356 Bytes left
    [I][macsniff.cpp:130] mac_add(): new   WiFi RSSI -78dBi -> MAC 93F5B4DAF1B4 -> Hash DBEB -> WiFi:9  BLTH:9 -> 51344 Bytes left
    """
    m = P.search(line)
    if m:
        data = {
            'new': True if m.group(1) == 'new' else False,
            'type': m.group(2),
            'rssi': int(m.group(3)),
            'mac': m.group(4),
        }
        return data
    else:
        return None


def get_serial():
    ser = serial.Serial()
    ser.port = sys.argv[1]  # TODO: to args
    ser.baudrate = baudrate  # TODO: to args
    ser.open()
    ser.flushInput()
    return ser


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


ser = get_serial()
wifis = {}
bles = {}
devs = {}
last_cleanup = time.time()
json_log = []

running = True

while running:
    try:
        line = ser.readline().decode("utf-8").strip()
    except UnicodeDecodeError as err:
        continue
    except serial.serialutil.SerialException as err:
        print(err)
        print('Exiting now')
        exit(1)
    #    line = str(line)
    line = line.strip()
    print(line)
    ts = get_now()
    if line.find('mac_add') > 0:
        data = parse_line(line)
        print(data)
        logdata = data.copy()
        logdata['time'] = ts
        json_log.append(json.dumps(logdata, default=json_serial))
        if data['type'].lower() in ['wifi', 'blth']:
            mac = data['mac']
            hit = (ts, data['rssi'])
            if mac not in devs:
                devs[mac] = data
                devs[mac].pop('new')
                # devs[mac].pop('type')
                devs[mac]['hits'] = [hit, ]
                devs[mac]['count'] = 1
            else:
                devs[mac]['count'] += 1
                if get_age(devs[mac]['hits'][-1][0]) >= 1.0:
                    devs[mac]['hits'].append(hit)
        # print(devs)
    if time.time() - last_cleanup > 5:  # TODO: last_cleanup to args
        to_remove = []
        for k, v in devs.items():
            age = get_age(v['hits'][-1][0])
            if age > MAX_AGE:
                # TODO: to args verbose
                print('GONE: {} {:6.2f} {:3d}'.format(k, age, v['count']))
                to_remove.append(k)
            else:
                # TODO: to args verbose
                print('HERE: {} {:6.2f} {:3d}'.format(k, age, v['count']))
        print()  # TODO: to args verbose
        # TODO: fname to args
        fname = datetime.datetime.utcnow().strftime('paxlog-%Y%m%d.txt')
        with open(fname, 'at') as f:
            for k in to_remove:
                r = devs.pop(k)
                r_json = json.dumps(r, default=json_serial)
                f.write(r_json + '\n')
                # print(json.dumps(r, indent=1, default=json_serial))
        fname = datetime.datetime.utcnow().strftime('paxlog-%Y%m%d.log')
        with open(fname, 'at') as f:
            f.write('\n'.join(json_log))
            json_log = []
        last_cleanup = time.time()
