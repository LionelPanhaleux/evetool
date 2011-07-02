import sqlite3
from functools import reduce

conn = sqlite3.connect('eve.db')

def item_name(id):
    cur = conn.execute('select typeName from invTypes where typeID=?', (id,))
    return cur.fetchall()[0][0]
    
def station_solar_system(id):
    cur = conn.execute('select solarSystemID from staStations where stationID=?', (id,))
    ret = cur.fetchall()
    if not ret: return None
    ret = ret[0]
    if not ret: return None
    ret = ret[0]
    return ret

def solar_system_jumps():
    cur = conn.execute('select fromSolarSystemID, toSolarSystemID from mapSolarSystemJumps')
    d = {}
    for jump in cur:
        d[jump[0]] = d.get(jump[0], ()) + (jump[1],)
    return d

def solar_system_id(name):
    cur = conn.execute('select solarSystemID from mapSolarSystems where solarSystemName=?', (name,))
    return cur.fetchall()[0][0]

jumps = solar_system_jumps()
    
def map_distance(id):
    done = set()
    rep = {0: set((id,))}
    for i in range(len(jumps)):
        done |= rep[i]
        rep[i+1] = set(filter(lambda a: a not in done, reduce(lambda a,b : a+b, [jumps[i] for i in rep[i]], ())))
        if not rep[i+1]: break
    return rep

def distance(ss_1, ss_2):
    done = set()
    last = set((ss_1,))
    for i in range(len(jumps)):
        if ss_2 in last: return i
        done |= last
        last = set(filter(lambda a: a not in done, reduce(lambda a,b : a+b, [jumps[i] for i in last], ())))
    return len(jumps)
    
def solar_systems_in_range(origin, rang):
    done = set()
    last = set((origin,))
    for i in range(rang):
        done |= last
        last = set(filter(lambda a: a not in done, reduce(lambda a,b : a+b, [jumps[i] for i in last], ())))
    return last

def closest_solar_systems(origin, num):
    done = set()
    last = set((origin,))
    for i in range(len(jumps)):
        done |= last
        last = set(filter(lambda a: a not in done, reduce(lambda a,b : a+b, [jumps[i] for i in last], ())))
        if len(last) >= num: break
    return last

def get_local_jump_table(solar_systems):
    ss = sorted(list(solar_systems))
    indexes = dict([(id, i) for i, id in enumerate(ss)])
    jump_table = [[distance(ss1, ss2) for ss2 in ss] for ss1 in ss]
    return indexes, jump_table

def get_solar_systems_regions(ss):
    cur = conn.execute('SELECT DISTINCT regionID from mapSolarSystems where solarSystemID in ({0})'.format(','.join(list(map(str, ss)))))
    return [t[0] for t in cur.fetchall()]
    
def get_solar_systems_dict(stations):
    return dict([(s, station_solar_system(s))for s in stations])

def region_stations(region):
    cur = conn.execute('SELECT stationID from staStations where regionID=?', str(region))
    return [t[0] for t in cur.fetchall()]
    
def solar_system_stations(ss):
    cur = conn.execute('SELECT stationID from staStations where solarSystemID=?', str(ss))
    return [t[0] for t in cur.fetchall()]

def station_name(id):
    cur = conn.execute('select stationName from staStations where stationID=?', (id,))
    return cur.fetchall()[0][0]

def load_solar_systems():
    cur = conn.execute('select solarSystemID,solarSystemName,regionID,security from mapSolarSystems')
    return dict([(r[0], {'name':r[1], 'regionid':r[2], 'security':r[3]}) for r in cur])

