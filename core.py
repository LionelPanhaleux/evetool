import datetime
import pickle
from gzip import GzipFile
from os import path
import os
import logging

import central
import db

def list_best_routes(origin, item):
    index, jump_table = db.get_local_jump_table(db.solar_systems_in_range(origin, 10))
    regions = db.get_solar_systems_regions(index.keys())
    orders = central.quicklook(item, regions)
    sss = db.get_solar_systems_dict(set([b['station'] for b in orders['buy']]) | set([s['station'] for s in orders['sell']]))
    for o in orders['buy']:
        o.update(solar_system=sss[o['station']])
    for o in orders['sell']:
        o.update(solar_system=sss[o['station']])
    orders['buy'] = [o for o in orders['buy'] if o['security'] >= 0.5 and o['solar_system'] in index.keys()]
    orders['sell'] = [o for o in orders['sell'] if o['security'] >= 0.5 and o['solar_system'] in index.keys()]
    orders['buy'].sort(key=lambda a: a['price'], reverse=True)
    orders['sell'].sort(key=lambda a: a['price'])
    
    best = []
    for b in orders['buy']:
        best += [ ( (s['station'], b['station']), 
                    float(b['price'] - s['price']) / max(1, jump_table[ index[b['solar_system']] ][ index[s['solar_system']] ]) )
                  for s in orders['sell'] if s['price'] < b['price'] ]
    best.sort(key=lambda a: a[1], reverse=True)
    return best

DUMP_PATH = 'orders.dump.gz'

logging.basicConfig(format='%(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger('evetool.core')

def init_load_orders(dat):
    logger.info('initiating orders data from {0}'.format(dat))
    if path.exists(DUMP_PATH):
        os.remove(DUMP_PATH)
    dic = central.get_dump(dat)
    pickle.dump((dat, dic), GzipFile(DUMP_PATH, 'wb'))
    
def load_orders():
    if not path.exists(DUMP_PATH):
        init_load_orders(datetime.date.today - timedelta(days=10))
        
    dat, dic = pickle.load(GzipFile(DUMP_PATH, 'rb'))
    logger.info('dump is from '+ str(dat))
    for i in range((datetime.date.today() - dat).days):
        new_dat = dat + datetime.timedelta(days=1)
        logger.info('fetching {0} dump from eve-central...'.format(new_dat))
        try:
            dic.update(central.get_dump(new_dat))
            dat = new_dat
        except central.NoSuchFile:
            logger.info('no dump available for {0}'.format(new_dat))
            break
    logger.info('orders data [] {0}'.format(dat))
    pickle.dump((dat, dic), GzipFile(DUMP_PATH, 'wb'))
    return dic
