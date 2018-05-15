import sys
import json

with open(sys.argv[1], 'rt') as f:
    lines = f.readlines()


def lightness(r):
    # Y = 0.2126 R + 0.7152 G + 0.0722 B
    y = int(r[:2], 16) * 0.2126 + int(r[2:4], 16) * 0.7152 + int(r[4:6], 16) * 0.0722
    return y


"""
{"rssi": "95", "mac": "C133B9CB", "hits": [["2018-05-14T11:23:20.053764+00:00", "95"], ["2018-05-14T11:23:26.634135+00:00", "93"], ["2018-05-14T11:23:33.188595+00:00", "94"], ["2018-05-14T11:23:46.063513+00:00", "96"]], "count": 4}
  [
    {id: 1, content: 'item 1', start: '2014-04-20'},
    {id: 2, content: 'item 2', start: '2014-04-14'},
    {id: 3, content: 'item 3', start: '2014-04-18'},
    {id: 4, content: 'item 4', start: '2014-04-16', end: '2014-04-19'},
    {id: 5, content: 'item 5', start: '2014-04-25'},
    {id: 6, content: 'item 6', start: '2014-04-27', type: 'point'}
  ]
"""

items = []
i = 0

for l in lines:
    d = json.loads(l)
    i += 1
    c = d['mac'][:6]
    if lightness(c) < 128:
        tc = '#ffffff'
    else:
        tc = '#000000'
    item = '{{ id: {}, content: "{}", start: "{}", style: "color: {}; background-color: #{};", '.format(
        i, d['mac'], d['hits'][0][0], tc, c)
    if len(d['hits']) > 1:
        item += 'end: "{}" }},'.format(d['hits'][-1][0])
        # print(item)
        items.append(item)
    else:
        item += 'type: "point" }},'.format()
        # do not show points
        # items.append(item)

with open('paxcounter-template.html', 'rt') as f:
    template = f.read()

template = template.replace('/***dataset***/', '\n'.join(items)[:-1])  # remove last point ','
with open('index.html', 'wt') as f:
    f.write(template)

