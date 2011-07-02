from http import client
from xml.etree import ElementTree
from io import StringIO
import sqlite3
import csv
import datetime
import os
from gzip import GzipFile

def quicklook(item_id, regions=[]):
    req = '/api/quicklook?typeid={0}'.format(item_id)
    for reg in regions:
        req += '&regionlimit={0}'.format(reg)
    con = client.HTTPConnection('api.eve-central.com')
    con.request('GET', req)
    buf = StringIO()
    buf.writelines([bs.decode() for bs in con.getresponse().readlines()])
    buf.seek(0)
    et = ElementTree.parse(buf)
    rep = {'buy':[], 'sell':[]}
    for order in et.getroot().find('quicklook').find('buy_orders'):
        rep['buy'].append({
            'region':   int(order.find('region').text),
            'station':  int(order.find('station').text),
            'security': float(order.find('security').text),
            'range':    int(order.find('range').text),
            'price':    float(order.find('price').text),
            'volume':   int(order.find('vol_remain').text),
            'min':      int(order.find('min_volume').text)})
    for order in et.getroot().find('quicklook').find('sell_orders'):
        rep['sell'].append({
            'region':   int(order.find('region').text),
            'station':  int(order.find('station').text),
            'security': float(order.find('security').text),
            'range':    int(order.find('range').text),
            'price':    float(order.find('price').text),
            'volume':   int(order.find('vol_remain').text),
            'min':      int(order.find('min_volume').text)})
    return rep

datetimeparser = str
durationparser = str

DICT_TYPE_KEYS = [(int, 'orderid'), 
             (int, 'regionid'), 
             (int, 'systemid'), 
             (int, 'stationid'), 
             (int, 'typeid'), 
             (bool, 'bid'), 
             (float, 'price'), 
             (int, 'minvolume'), 
             (int, 'volremain'), 
             (int, 'volenter'), 
             (datetimeparser, 'issued'), 
             (durationparser, 'duration'), 
             (int, 'range')]

DICT_KEYS = [tk[1] for tk in DICT_TYPE_KEYS]


def line_to_entry(line):
    return (DICT_TYPE_KEYS[0][0](line[DICT_TYPE_KEYS[0][1]]), dict(
        [(type_key[1], type_key[0](line[type_key[1]])) for type_key in DICT_TYPE_KEYS[1:]]))


def load_dump(dump_path):
    fil = open(dump_path)
    fil.readline()
    rdr = csv.DictReader(fil, DICT_KEYS)
    return dict([line_to_entry(line) for line in csv.DictReader(fil, DICT_KEYS)])


class NoSuchFile(Exception):
    def __init__(self, *args, **kwargs):
        super(NoSuchFile, self).__init__(*args, **kwargs)


def get_dump(dat):
    name = str(dat) + '.dump.gz'
    con = client.HTTPConnection('eve-central.com')
    con.request('GET', '/dumps/' + name)
    res = con.getresponse()
    if res.status != 200:
        raise NoSuchFile('dump file not found: ' + name)
    f = open(name, 'wb')
    f.writelines(res.readlines())
    f.close()
    csvname = name[:-3] + '.csv'
    f = open(csvname, 'w')
    g = GzipFile(name)
    f.writelines([bs.decode() for bs in g.readlines()])
    f.close()
    dic = load_dump(csvname)
    os.remove(name)
    os.remove(csvname)
    return dic
