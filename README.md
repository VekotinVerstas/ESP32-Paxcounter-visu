# ESP32-Paxcounter-visu

First run `paxcounter_readserial.py` like this on Mac:

`python paxcounter_readserial.py /dev/tty.SLAB_USBtoUART`

Or on Raspberry Pi / other linux:

`python paxcounter_readserial.py /dev/ttyUSB0`

Command writes lines like this to a file called `paxlog-%Y%m%d`:

```
{"mac": "1D457812", "hits": [["2018-05-15T10:54:51.646436+00:00", "87"]], "rssi": "87", "count": 2}
{"mac": "4E4A2010", "hits": [["2018-05-15T10:54:54.145062+00:00", "93"], ["2018-05-15T10:55:00.538629+00:00", "93"]], "rssi": "93", "count": 3}
{"mac": "85A0CBEF", "hits": [["2018-05-15T10:55:13.947188+00:00", "88"], ["2018-05-15T10:55:33.731516+00:00", "89"], ["2018-05-15T10:55:37.125710+00:00", "88"]], "rssi": "88", "count": 5}
{"mac": "66370CF6", "hits": [["2018-05-15T10:55:51.819995+00:00", "72"]], "rssi": "72", "count": 1}
{"mac": "A334A2E4", "hits": [["2018-05-15T10:55:05.586241+00:00", "91"], ["2018-05-15T10:55:59.504123+00:00", "90"]], "rssi": "91", "count": 2}
```

After running this a while, create web visualisation from the data:

`python paxlog2vis.py paxlog-20180515.txt`

Then run

`python -m SimpleHTTPServer 5000`

and open [http://127.0.0.1:5000]() in your browser.

