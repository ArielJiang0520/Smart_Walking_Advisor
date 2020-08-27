import sys
sys.path.append('./')
from DataConnecter import Database
sys.path.append('./data analyzer/location analyzer')
import DistanceCalculator
from datetime import timedelta, datetime

def get_calendar_events_list(uid, current_time):
    d = Database()
    query = '''SELECT event_name, location, start_time FROM `calendar`
WHERE (`uid` = {0}) AND (start_time >= \"{1}\")
ORDER BY start_time LIMIT 10'''.format(uid, current_time.strftime('%Y-%m-%d %H:%M:%S'))
    d.cursor.execute(query)
    result = []
    for e in d.cursor:
        result.append(e[2].strftime('%m/%d %H:%M')+": "+"\""+e[0]+"\""+" at "+e[1])
    return result

def find_next_calendar_event(uid, current_time):
    d = Database()
    query = '''SELECT event_name, location, start_time FROM `calendar`
WHERE (`uid` = {0}) AND (start_time >= \"{1}\")
ORDER BY start_time LIMIT 1'''.format(uid, current_time.strftime('%Y-%m-%d %H:%M:%S'))
    d.cursor.execute(query)
    try:
        return next(iter(d.cursor))
    except:
        return None

def add_event(uid,event_name,location,start_time,duration):
    #duration in minutes
    query = '''INSERT IGNORE INTO `calendar`(uid,event_name,location,start_time,end_time)
VALUES(%s, %s, %s, %s, %s)'''
    val = (uid, event_name, location, start_time, start_time+timedelta(minutes=duration))
    d = Database()
    d.cursor.execute(query, val)
    d.db.commit()

#in mile
#TODO
def get_ideal_distance(uid, current_time, current_steps, goal, max_distance):
    return DistanceCalculator.steps_to_mile(goal-current_steps)

# hour=0
# for event,address in [('class',"Ring Rd Irvine, CA 92617 USA"), ('meeting with study group','18100 Culver Dr, Irvine, CA 92612'),
#             ('dinner with friends','4535 Campus Dr, Irvine, CA 92612')]:
#     hour+=2
#     add_event("1",event,address, datetime.now()+timedelta(hours=hour),60)
# add_event("1","grocery shopping","71 Technology Dr, Irvine, CA 92618",datetime.now()+timedelta(minutes=60), 60)
