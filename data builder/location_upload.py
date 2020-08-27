import json
from pathlib import Path
from datetime import datetime
import database_getter
import sys
sys.path.append('./')
from DataConnecter import Database
sys.path.append('./data analyzer/location analyzer')
import YelpAPI
import FindPlaces, DistanceCalculator

def has_event_type(uid,lat,long,types):
    # types is string
    types = types.split(',')
    home = database_getter.get_user_home_address(uid)
    school = database_getter.get_user_school_address(uid)
    work = database_getter.get_user_work_address(uid)
    if 'gym' in types or 'fitness' in types:
        return 'gym'
    elif 'coffee' in types or 'cafe' in types:
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
        return 'none'

def update_behavior_pattern(uid, start_time, event, col_str):
    d = Database()
    query = '''UPDATE `behavior pattern`
    SET {}last_time="{}"
    WHERE `uid` = "{}" AND `event`="{}"
    '''.format(col_str, start_time, uid, event)
    print(query)
    d.cursor.execute(query)
    d.db.commit()

def update_location_frequency(uid, start_time, end_time, place_id):
    d = Database()
    query = '''
INSERT INTO `location frequency`(uid,place_id{0})
VALUES ("{1}","{2}"{3})
ON DUPLICATE KEY UPDATE '''
    col_str = val_str = update_str = ""
    bp_col_str = ""
    end_time_hour = end_time.hour + 1 if start_time.hour <= end_time.hour else end_time.hour+25
    for h in range(start_time.hour, end_time_hour):
        h = h % 24
        col_str+=",{0}_{1}_freq, {0}_{1}_recent_time".format(h,h+1)
        val_str+=",1,\"{}\"".format(start_time)
        update_str+="{0}_{1}_freq = {0}_{1}_freq + 1, {0}_{1}_recent_time = \"{2}\",".format(h,h+1,start_time)
        bp_col_str+="{0}_{1}_freq = {0}_{1}_freq + 1,".format(h,h+1)
    update_str = update_str.rstrip(',')
    query = query.format(col_str,uid,place_id,val_str) + update_str
    #print(query)
    d.cursor.execute(query)
    d.db.commit()
    event_type = database_getter.get_event_type(place_id)
    if event_type != "none":
        update_behavior_pattern(uid, start_time, event_type, bp_col_str)

def update_location_index(uid, place_id, address, location_name, lat, long, stayed_time):
    d = Database()
    query = '''SELECT COUNT(*) FROM `location index`
WHERE `uid` = "{}" AND `place_id` = "{}"'''.format(uid, place_id)
    d.cursor.execute(query)
    if int(next(iter(d.cursor))[0]) == 0:
        types = ",".join(YelpAPI.get_categories_from_name_and_address(\
            name=location_name,address=address))
        if types != "":
            types += "," + ",".join(FindPlaces.get_place_types(place_id))
        else:
            types += ",".join(FindPlaces.get_place_types(place_id))
        event_type = has_event_type(uid,lat,long,types)
        query = '''INSERT IGNORE INTO `location index`(
        `uid`, `place_id`, `location_name`, `address`, `types`, `lat`, `long`,
        `ave_staying_time`, `total_freq`, `associate_event`)
        VALUES ("{}","{}","{}","{}","{}",{},{},{},{},"{}")'''.format(\
        uid, place_id, location_name, address.replace('\n',' '), \
        types, lat, long, stayed_time, 1, event_type)
        d.cursor.execute(query)
        d.db.commit()
    else:
        print("location already in index")
        query = '''UPDATE `location index`
SET `ave_staying_time` = ({}+`total_freq`*`ave_staying_time`)/(`total_freq`+1), `total_freq`=`total_freq` + 1
WHERE `place_id` = "{}" AND `uid` = "{}"'''.format(stayed_time, place_id, uid)
        d.cursor.execute(query)
        d.db.commit()

def update_location_history(json_file,uid):
    with open(json_file) as read_file:
        data = json.load(read_file)
    d = Database()
    for tl in data['timelineObjects']:
        if 'placeVisit' in tl:
            try:
                start_timestamp = round(int(tl['placeVisit']['duration']['startTimestampMs'])/1000)
                end_timestamp = round(int(tl['placeVisit']['duration']['endTimestampMs'])/1000)
                start_datetime = datetime.fromtimestamp(start_timestamp)
                end_datetime = datetime.fromtimestamp(end_timestamp)
                stayed_time = round((end_datetime - start_datetime).total_seconds()/60)
                if 'childVisits' in tl['placeVisit']:
                    place = tl['placeVisit']['childVisits'][0]['location']
                else:
                    place = tl['placeVisit']['location']
                address = place['address']
                location_name = place['name']
                place_id = place['placeId']
                lat = place['latitudeE7']/1e7
                long = place['longitudeE7']/1e7
                query = '''SELECT COUNT(*) FROM `location history`
    WHERE `uid` = "{}" AND `start_time` = "{}"'''.format(uid,start_datetime)
                d.cursor.execute(query)
                if int(next(iter(d.cursor))[0]) == 0:
                    print("{} at {} is new info".format(location_name, start_datetime))
                    update_location_index(uid, place_id, address, location_name, lat, long, stayed_time)
                    update_location_frequency(uid, start_datetime, end_datetime, place_id)
                query = '''
    INSERT IGNORE INTO `location history`(uid, start_time, end_time, place_id,stayed_time)
    VALUES (%s, %s, %s, %s, %s)'''
                val = (uid, start_datetime, end_datetime, place_id,stayed_time)
                d.cursor.execute(query,val)
                d.db.commit()
            except KeyError:
                print("some bad location happened")
                pass

#print(",cat,dog".split(','))
# path = Path.cwd()/"data builder"/"data"/"2020_FEBRUARY_4.json"
# update_location_history(path,"1")
path = Path.cwd()/"data builder"/"data"/"2020_FEBRUARY_4.json"
update_location_history(path,"1")
# path2 = Path.cwd()/"data builder"/"data"/"2020_FEBRUARY_3.json"
# update_location_history(path2,"1")
