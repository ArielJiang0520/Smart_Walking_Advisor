import sys
import database_getter
sys.path.append('./')
from DataConnecter import Database
sys.path.append('./data builder/cluster')
import theta


# def is_in_clusters(uid, place_id) -> bool:
#     d = Database()
#     query = '''SELECT `uid`,`cid` FROM `cluster`
# WHERE `uid` = "{}" AND `members` LIKE "%{}%"'''.format(uid, place_id)
#     d.cursor.execute(query)
#     try:
#         next(iter(d.cursor))
#         return True
#     except StopIteration:
#         return False

def get_all_clusters(uid):
    d = Database()
    query = f'''SELECT * FROM `cluster`
WHERE `uid` = "{uid}"'''
    d.cursor.execute(query)
    clusters = []
    for c in d.cursor:
        clusters.append(c)
    return clusters
    # uid 0 cid 1 members 2 lat,long (3,4) dist_to_center lat,long (5,6)
    # dominant types 7 ave staying time 8 frequency 9

def get_cid(uid, place_id, lat, long, types):
    d = Database()
    #associate_event = database_getter.has_event_type(uid, lat, long, types)

    if database_getter.is_school_event(uid, lat, long):
        query = f'''SELECT `cid` FROM `cluster`
WHERE `uid` = "{uid}" AND `event_type` = "school"'''
        d.cursor.execute(query)
        return next(iter(d.cursor))[0]

    type_list = []
    for t in types:
        type_list.append(f'(`dominant_types` LIKE "%{t}%")')
    type_str = ' OR '.join(type_list)
    query = f'''SELECT `cid` FROM `cluster`
WHERE `uid` = "{uid}" AND
(ABS( ABS({lat}-`center_lat`) - `ave_dist_to_center_lat`)
+ ABS( ABS({long}-`center_long`) - `ave_dist_to_center_long`))
< {theta.CLOSE_LAT_LONG} AND ({type_str})
'''
    #print(query)
    d.cursor.execute(query)
    try:
        return next(iter(d.cursor))[0]
    except StopIteration:
        query = f'''SELECT `cid`,`dominant_types` FROM `cluster`
WHERE `uid` = "{uid}" AND ({type_str})
'''
        #print(query)
        d.cursor.execute(query)
        for cid, t in d.cursor:
            t_list = t.split(",")
            if len(set(t_list)&set(types))>=3:
                return cid
        return None

def get_staying_time(uid,cid):
    d = Database()
    query = f'''SELECT `ave_staying_time` FROM `cluster`
WHERE `uid` = "{uid}" AND `cid` = "{cid}"'''
    d.cursor.execute(query)
    return float(next(iter(d.cursor))[0])

# cid = get_cid("1",'ChIJVRvzNQze3IARlsfGYNVfU-M',1,-1,['cafe','coffee','restaurant'])
# print(cid)

# print(get_staying_time("1","1"))
