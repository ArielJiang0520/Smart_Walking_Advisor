import sys
sys.path.append('./scorer')
import scorer
sys.path.append('./searcher')
from search import search
sys.path.append('/data builder')
import database_getter, calendar_getter
sys.path.append('/data builder/location analyzer')
import DistanceCalculator

from datetime import datetime

def get_context(uid, current_steps, current_location, current_time):
    user_max_distance = database_getter.get_user_max_distance(uid)

    user_goal = database_getter.get_user_goal(uid)

    remaining_distance = DistanceCalculator.steps_to_mile((
        user_goal - current_steps))

    ideal_distance = calendar_getter.get_ideal_distance(uid,
        current_time, current_steps, user_goal, user_max_distance)

    events = database_getter.is_event_time(uid, current_time)
    events-=set(['home','school','work'])

    try:
        event_name, event_location, event_time = \
            calendar_getter.find_next_calendar_event(uid, current_time)
        spare_time = round((event_time-current_time).seconds/60)
        travel_distance, _ = DistanceCalculator.get_distance_and_time(
            current_location, event_location)
        travel_distance = DistanceCalculator.meter_to_mile(travel_distance)
        if travel_distance > 5:
            MODE = 'driving'
        else:
            MODE = 'walking'
    except:
        spare_time = float('inf')
        event_location, event_time = None, None
        MODE = 'walking'

    return [user_max_distance, ideal_distance,
            event_location, event_time,
            spare_time, events, MODE]

def main_search(uid, current_steps, current_location, current_time):
    context=get_context(uid,current_steps,current_location,current_time)
    return search(uid, context[0], context[1],
        current_location, current_time,
        context[2], context[3],
        context[4], context[5], context[6])

# recommendations = main_search(
#     "1", 6000, (33.65972,-117.83740000000003), datetime.now())

def current_mode(uid, current_time):
    if database_getter.is_in_schedule(uid):
        return 'schedule'
    elif current_time.hour in database_getter.get_rest_time(uid):
        return 'resting'
    elif database_getter.is_in_trip(uid):
        return 'trip'
    else:
        return 'rec'

# def main(uid, current_steps, current_location, current_time):
#
#     IN_TRIP = False
#     IN_SCHEDULE = False
#
#     RESTING = current_time.hour in database_getter.get_rest_time(uid)
#
#     user_max_distance = database_getter.get_user_max_distance(uid)
#
#     user_goal = database_getter.get_user_goal(uid)
#
#     remaining_distance = DistanceCalculator.steps_to_mile((
#         user_goal - current_steps))
#
#     while not IN_TRIP and not IN_SCHEDULE and not RESTING:
#         ideal_distance = calendar_getter.get_ideal_distance(uid,
#             current_time, user_goal, current_steps, user_max_distance)
#
#         events = database_getter.is_event_time(uid, current_time)
#         events-=set(['home','school','work'])
#
#         try:
#             event_name, event_location, event_time = \
#                 calendar_getter.find_next_calendar_event(uid, current_time)
#             spare_time = round((event_time-current_time).seconds/60)
#             travel_distance, _ = DistanceCalculator.get_distance_and_time(
#                 current_location, event_location)
#             travel_distance = DistanceCalculator.meter_to_mile(travel_distance)
#             if travel_distance > 5:
#                 MODE = 'driving'
#             else:
#                 MODE = 'walking'
#         except StopIteration:
#             spare_time = float('inf')
#             event_location, event_time = None
#             MODE = 'walking'
#
#         search(uid, user_max_distance, ideal_distance,
#             current_location, current_time,
#             event_location, event_time,
#             spare_time, events, MODE)
#
#         IN_TRIP = True

#main("1", 5000, (33.65972,-117.83740000000003), datetime.now())


# import pickle
# import math
#
# uid = "1"
# recommendations = main_search(
#                     uid,
#                     database_getter.get_user_current_step(uid),
#                     database_getter.get_user_current_location(uid),
#                     datetime.now())
#
# with open("temp.txt", "wb") as f:
#     pickle.dump(recommendations, f)
