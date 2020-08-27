import sys
sys.path.append('./')
from DataConnecter import Database
from collections import defaultdict
from pathlib import Path
import numpy as np
from datetime import datetime
sys.path.append('./data analyzer/location analyzer')
import DistanceCalculator

EVENT_TYPES = {
    'coffee':['cafe','coffee'],
    'meal':['restaurant'],
    'work':[],
    'grocery':['grocery','supermarket','department_store'],
    'school':[],
    'home':[]
}

def get_user_current_location(uid):
    d=Database()
    query=f'''SELECT `current_location_lat`,`current_location_long`
    FROM `active data`
    WHERE `uid` = "{uid}"'''
    d.cursor.execute(query)
    return next(iter(d.cursor))

def get_user_trip_destination(uid):
    d=Database()
    query=f'''SELECT `destination` FROM `active data`
    WHERE `uid` = "{uid}"'''
    d.cursor.execute(query)
    try:
        return next(iter(d.cursor))[0]
    except StopIteration:
        return None

def get_user_current_step(uid):
    d=Database()
    query=f'''SELECT `current_step` FROM `active data`
    WHERE `uid` = "{uid}"'''
    d.cursor.execute(query)
    try:
        return int(next(iter(d.cursor))[0])
    except StopIteration:
        return None

## TODO
def is_in_schedule(uid):
    return False

def is_in_trip(uid):
    d=Database()
    query=f'''SELECT `in_trip` FROM `active data`
    WHERE `uid` = "{uid}"'''
    d.cursor.execute(query)
    try:
        return int(next(iter(d.cursor))[0]) != 0
    except StopIteration:
        return None

def is_school_event(uid,lat,long):
    school = get_user_school_address(uid)
    return DistanceCalculator.get_distance((lat,long),school) <= 650

def has_event_type(uid,lat,long,types):
    home = get_user_home_address(uid)
    school = get_user_school_address(uid)
    work = get_user_work_address(uid)
    if 'coffee' in types or 'cafe' in types:
        return 'coffee'
    elif 'restaurant' in types:
        return 'meal'
    elif 'grocery' in types or 'department_store' in types or 'supermarket' in types:
        return 'grocery'
    elif DistanceCalculator.get_distance((lat,long),school) <= 650:
        return 'school'
    elif DistanceCalculator.get_distance((lat,long),home) <= 100:
        return 'home'
    elif DistanceCalculator.get_distance((lat,long),work) <= 500:
        return 'work'
    else:
        return None

def _get_bp_as_array(uid,event_type):
    d = Database()
    col_str = []
    for hour in range(24):
        col_str.append(f"`{hour}_{hour+1}_freq`")
    query = '''SELECT {} FROM `behavior pattern`
WHERE `uid` = "{}" AND `event` = "{}"'''.format(",".join(col_str),\
    uid,event_type)
    d.cursor.execute(query)
    array = []
    for row in d.cursor:
        for number in row:
            array.append(number)
    return array

def is_event_time(uid, current_time):
    #exclude 'home'
    current_hour = current_time.hour
    result = []
    for e in EVENT_TYPES:
        array = _get_bp_as_array(uid, e)
        std_diff = np.array((array-np.mean(array))/np.std(array))
        hours = [n for n,i in enumerate(std_diff) if i >= 1]
        if current_hour in hours:
            result.append(e)
    result = _filter_events_by_times(uid,result,current_time)
    return set(result)

def _filter_events_by_times(uid,events,current_time):
    exclude = []
    for e in events:
        d = Database()
        query = f'''SELECT `happened_times`,`last_time`,`normal_frequency`
FROM `behavior pattern` WHERE `uid` = "{uid}" AND `event` = "{e}"'''
        d.cursor.execute(query)
        happened_times, last_time, normal_frequency = next(iter(d.cursor))
        if e == 'meal':
            if int(happened_times) >= 3:
                exclude.append(e)
        elif e == 'coffee':
            if int(happened_times) >= 1:
                exclude.append(e)
        elif ((current_time - last_time).total_seconds()/3600) \
            < normal_frequency*0.5:
            exclude.append(e)
    return [e for e in events if e not in exclude]

def get_rest_time(uid):
    array = _get_bp_as_array(uid, 'home')
    # print(array)
    # print(np.mean(array),np.std(array))
    std_diff = np.array((array-np.mean(array))/np.std(array))
    # print(std_diff)
    stay_home_hours = [i for i in range(24) if std_diff[i] > 0.5]
    return stay_home_hours

def get_event_type(place_id):
    d=Database()
    query='''SELECT `associate_event` FROM `location index`
    WHERE `place_id` = "{}"'''.format(place_id)
    d.cursor.execute(query)
    return str(next(iter(d.cursor))[0])

def contains_visited_places(uid, id_list):
    '''returns the number of id in id_list that has been visited before'''
    d = Database()
    result = []
    for id in id_list:
        query = '''SELECT COUNT(*) FROM `location index`
    WHERE `place_id` = "{}"'''.format(id)
        d.cursor.execute(query)
        if int(next(iter(d.cursor))[0]) >= 1:
            result.append(id)
    return result

def get_location_info(uid, place_id):
    d = Database()
    query = '''SELECT `location_name`,`address`,`lat`,`long`,`types`,
`ave_staying_time`,`total_freq`,`associate_event`
FROM `location index`
WHERE `uid`="{}" AND `place_id` = "{}"'''.format(uid, place_id)
    d.cursor.execute(query)
    # location name 0 address 1 lat,long (2,3) types 4
    #ave_staying_time 5, total_freq 6, associate_event 7
    return next(iter(d.cursor))

def is_in_address_type(type):
    d = Database()
    query='''SELECT COUNT(*) FROM `address type`
WHERE`type`="{}"'''.format(type)
    d.cursor.execute(query)
    return int(next(iter(d.cursor))[0]) > 0

def get_user_home_id(uid):
    d = Database()
    query='''SELECT `home_id` FROM `user` WHERE `uid` = "{}"'''.format(uid)
    d.cursor.execute(query)
    return str(next(iter(d.cursor))[0])

def get_user_home_address(uid):
    d = Database()
    query='''SELECT `home_address` FROM `user` WHERE `uid` = "{}"'''.format(uid)
    d.cursor.execute(query)
    return str(next(iter(d.cursor))[0])

def get_user_school_address(uid):
    d = Database()
    query='''SELECT `school_address` FROM `user` WHERE `uid` = "{}"'''.format(uid)
    d.cursor.execute(query)
    return str(next(iter(d.cursor))[0])

def get_user_work_address(uid):
    d = Database()
    query='''SELECT `work_address` FROM `user` WHERE `uid` = "{}"'''.format(uid)
    d.cursor.execute(query)
    return str(next(iter(d.cursor))[0])

def get_location_with_event_as_list(uid,event):
    d = Database()
    query = '''SELECT `place_id` FROM `location index`
WHERE `uid` = "{}" AND `associate_event` = "{}"'''.format(uid,event)
    d.cursor.execute(query)
    result = [id[0] for id in d.cursor]
    return result

def get_location_index_as_list(uid):
    d = Database()
    query = '''SELECT `place_id` FROM `location index`
WHERE `uid` = "{}"'''.format(uid)
    d.cursor.execute(query)
    result= [id[0] for id in d.cursor]
    return result

def get_user_max_distance(uid):
    d = Database()
    d.cursor.execute('''SELECT `max_distance` FROM `user` WHERE `uid` = "{}" LIMIT 1'''.format(uid))
    return int(next(iter(d.cursor))[0])

def get_user_goal(uid):
    d = Database()
    d.cursor.execute('''SELECT `goal` FROM `user` WHERE `uid` = "{}" LIMIT 1'''.format(uid))
    return int(next(iter(d.cursor))[0])

def is_past_location(place_id):
    d = Database()
    query = '''SELECT `location_name` FROM `location index`
WHERE `place_id` = "{}"'''.format(place_id)
    d.cursor.execute(query)
    try:
        return str(next(iter(d.cursor))[0])
    except StopIteration:
        return None
