from Recommendation import Recommendation
from Route import Route

import sys

sys.path.append('./scorer')
import calendar_scorer

sys.path.append('./data builder')
import database_getter

sys.path.append('./data analyzer/location analyzer')
import Geocoding, DistanceCalculator, FindPlaces

from datetime import datetime, timedelta
from collections import defaultdict


def calendar_search(uid, current_steps, current_time, current_location, \
    event_time, event_location):
    estimate_address = Geocoding.get_address(current_location)
    fp = open(log, "w+")

    fp.write('''
    It is currently {0}
    You are at lat: {1}, long: {2}
    Your estimate location: {3}
    Your current steps: {4}, {5} steps away from your goal step
    '''.format(current_time.strftime('%Y-%m-%d %H:%M:%S'),\
                current_location[0],current_location[1],\
                estimate_address,current_steps,\
                database_getter.get_user_goal(uid) - current_steps))

    event_distance, event_travel_time = DistanceCalculator.get_distance_and_time(\
        current_location, event_location)
    event_travel_time = round(event_travel_time/60)

    spare_time = round((event_time-current_time).seconds/60)

    fp.write('''
    Your next event "{0}" will start at {1}
    at location "{2}"
    It is {3} miles away. It will take you {4} minutes to walk there.
    You have {5} minutes to spare on the road
    '''.format(event_name, event_time.strftime('%Y-%m-%d %H:%M:%S'), \
    event_location.replace("\n"," "),\
    DistanceCalculator.meter_to_mile(event_distance),\
    event_travel_time,spare_time-event_travel_time))

    #in miles
    user_max_distance = MaxDistance.get_user_max_distance(uid)
    remaining_distance = DistanceCalculator.steps_to_mile((\
        MaxDistance.get_user_goal(uid) - current_steps))

    if DistanceCalculator.meter_to_mile(event_distance) > user_max_distance:
        fp.write('''
        Your next event is more than {:03.2f} miles away.
        It exceeds your physical limit, I do not suggest you walk there.
        '''.format(user_max_distance))
        return

    elif spare_time <= event_travel_time:
        fp.write('''
        It shows that it takes at least {} minutes to walk to your next event.
        You barely have enough time! Start walking now or take some kind of transporation!
        Of course I would not suggest any stops on the way!
        '''.format(event_travel_time))
        return

    else:
        fp.write('''
        Your next event is within your max capacity: {:03.2f} miles, you can walk there!
        Why not stop somewhere on the way if you have time?
        '''.format(user_max_distance))

        fp.write('''
        Calculating possible quick stops on the way...
        ''')

        # find routes
        routes = defaultdict(Route)
        user_types = LocationType.get_user_types(uid)
        type_score = calendar_scorer.INIT_TYPE_SCORE
        for type in (list(user_types[0])+calendar_scorer.GOOD_STOP_TYPES):
            if type not in calendar_scorer.BAD_STOP_TYPES:
                for place in FindPlaces.get_nearby_places(location=current_location,
                    type=type, radius=min(DistanceCalculator.mile_to_meter(\
                    remaining_distance)*calendar_scorer.DISTANCE_REGULARIZED,\
                    DistanceCalculator.mile_to_meter(\
                    user_max_distance)*calendar_scorer.DISTANCE_REGULARIZED),\
                    exclude_kw=calendar_scorer.BAD_STOP_TYPES):
                    routes[place[1]] = Route(stop=place, origin=current_location,\
                        dest=event_location, init_score=type_score)
            type_score = calendar_scorer.type_score_func(type_score)

        #scoring part
        for k,r in routes.items():
            #goal distance scoring
            r.score += calendar_scorer.goal_distance_func(\
                DistanceCalculator.mile_to_meter(\
                remaining_distance), r.origin_to_stop[0]+r.stop_to_dest[0])
            #location history scoring
            if LocationHistory.is_past_location(r.stop_id):
                r.score += calendar_scorer.past_location_func()
            #good type scoring
            if (set(r.stop_types) & set(calendar_scorer.GOOD_STOP_TYPES)):
                r.score += calendar_scorer.good_type_func(\
                    len(set(calendar_scorer.GOOD_STOP_TYPES) & set(r.stop_types)))
            #distance too long penalty
            if r.origin_to_stop[0] > DistanceCalculator.mile_to_meter(\
                user_max_distance)*(1/calendar_scorer.DISTANCE_REGULARIZED):
                r.score += calendar_scorer.SEVERE_PENALTY
            #min staying time penalty
            if (spare_time - r.total_time) < calendar_scorer.MIN_STAYING_TIME:
                r.score += calendar_scorer.SEVERE_PENALTY

        results_len = len(routes)
        if len(routes) >= calendar_scorer.K_RESULTS:
            results_len = calendar_scorer.K_RESULTS
        else:
            if len(routes) == 0:
                fp.write('''
                Sorry, there's no available stops on the way that could keep you
                from being late to your next event :( Please try later
                ''')

        recommendations = []
        for n,k in enumerate(sorted(\
            routes.keys(), key=lambda x:routes[x].score, reverse=True)[:results_len]):
            r = routes[k]
            if r.score > 0:
                fp.write('''
                Suggestion {}:
                    "{}" at "{}"
                    Primary location type: "{}"
                    It is {:.1f} miles away. It takes {} steps to walk there.
                    ===========================================================
                    It will take you {} minutes to walk there.
                    You will arrive at {} if you leave now.
                    ===========================================================
                    After completing this walk, your steps will be {} for today.
                    ===========================================================
                    You can hang at this location for {} minutes before you start walking to your scheduled event.
                    If you finish the entire trip, you will have walked {} steps today
                    '''.format(n+1,\
                    r.stop_name, r.stop_address,\
                    r.stop_types[0], \
                    DistanceCalculator.meter_to_mile(r.origin_to_stop[0]), \
                    r.step_to_stop,\
                    round(r.origin_to_stop[1]/60),(current_time+timedelta(\
                    seconds=r.origin_to_stop[1])).strftime('%Y-%m-%d %H:%M:%S'),\
                    r.step_to_stop+current_steps,\
                    spare_time-r.total_time, r.step_to_dest+current_steps))

                if r.step_to_dest+current_steps >= MaxDistance.get_user_goal(uid):
                    fp.write('''
                    You will complete your daily goal after this walk!
                    ''')
                else:
                    fp.write('''
                    You will be {} steps away from your goal for today!
                    '''.format(MaxDistance.get_user_goal(uid)-(r.step_to_dest+current_steps)))

                rec=Recommendation(\
                    uid=uid, type=0,\
                    start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),\
                    duration=r.origin_to_stop[1],\
                    place_id=r.stop_id, place_name=r.stop_name,\
                    place_address=r.stop_address,\
                    place_types=r.stop_types,steps=r.step_to_stop
                )
                recommendations.append(rec)
                Recommendation.add_to_db(rec)

        return recommendations

#calendar_search("1",datetime.now(),(33.6532819,-117.8395018),2000, "log.txt")
