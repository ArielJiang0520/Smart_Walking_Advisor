from Recommendation import Recommendation
from Route import Route
import sys
sys.path.append('./scorer')
import scorer
sys.path.append('./data builder')
import database_getter, cluster_getter
sys.path.append('./data analyzer/location analyzer')
import Geocoding, DistanceCalculator, FindPlaces
from datetime import datetime, timedelta
from collections import defaultdict

def search(uid, max_distance, ideal_distance,
    current_location, current_time,
    event_location, event_time,
    spare_time, bias, mode):

    print('searching....')
    print('event_location',event_location)
    print('event_time',event_time)
    print('spare_time',spare_time)
    print('bias',bias)

    radius = DistanceCalculator.mile_to_meter(\
        min(ideal_distance, max_distance))*\
        scorer.DISTANCE_REGULARIZED

    print('radius',radius)

    keyword = set()
    for b in bias:
        keyword = keyword | set(database_getter.EVENT_TYPES[b])

    if spare_time < scorer.MAX_SPARE_TIME:
        keyword = keyword | scorer.SHORT_STOP_TYPES
    else:
        keyword = keyword | scorer.LONG_STOP_TYPES

    routes = defaultdict(Route)

    # search nearby places around both start ptr and dest ptr
    for location in [current_location,event_location]:
        if location != None:
            for k in keyword:
                for place in FindPlaces.get_nearby_places(
                    location=location, radius=radius, keyword=k):
                    if place[1] not in routes:
                        routes[place[1]] = Route(stop=place, origin=current_location,
                            dest=event_location, mode=mode)
                        routes[place[1]].set_staying_time(uid)

    for stop_id,route in routes.items():
        print("=================",route.stop_name,"=================")
        print("goal distance scoring")
        route.add_score(scorer.goal_distance_func(
            DistanceCalculator.mile_to_meter(
                ideal_distance), route.total_dist
        ))
        print(route.score)
        print("location history scoring")
        route.add_score(scorer.past_location_func(
            database_getter.is_past_location(route.stop_id)
        ))
        print(route.score)
        print("staying time scoring")
        route.add_score(scorer.staying_time_func(
            spare_time - route.total_time, route.staying_time
        ))
        print(route.score)
        print("event bias scoring")
        route.add_score(scorer.event_bias_func(bias, route.stop_types))
        print(route.score)


    recommendations = []
    for stop_id,route in sorted(
        routes.items(), key=lambda x:x[1].score, reverse=True)[:3]:
        report = '''
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
            '''.format(
                    route.stop_name, route.stop_address,
                    route.stop_types[0],
                    DistanceCalculator.meter_to_mile(route.origin_to_stop[0])\
                        if route.origin_to_stop[0] != 0 else DistanceCalculator.meter_to_mile(
                        route.stop_to_dest[0]),
                    route.step_to_stop \
                        if route.step_to_stop != 0 else route.step_to_dest,
                    round(route.origin_to_stop[1]/60) \
                        if route.origin_to_stop[1] != 0 else round(route.stop_to_dest[1]/60),
                    (current_time+timedelta(
                        seconds=route.origin_to_stop[1])).strftime('%Y-%m-%d %H:%M:%S')\
                        if route.origin_to_stop[1] != 0 else (current_time+timedelta(
                            seconds=route.origin_to_stop[1])).strftime('%Y-%m-%d %H:%M:%S'),
                    route.step_to_stop+database_getter.get_user_current_step(uid)\
                        if route.step_to_stop != 0 \
                        else route.step_to_dest+database_getter.get_user_current_step(uid),
                    spare_time-route.trip_time
                )
        print(report)

        rec=Recommendation(
            uid=uid, type=0 if not bias else 1,
            start_time=current_time,
            duration=route.origin_to_stop[1] \
                if route.origin_to_stop[1] != 0 else route.step_to_stop[0],
            place_id=route.stop_id,
            place_name=route.stop_name,
            place_address=route.stop_address,
            place_types=route.stop_types,
            steps=route.step_to_stop \
                if route.step_to_stop != 0 else route.step_to_dest,
            report=report
        )
        recommendations.append(rec)
        Recommendation.add_to_db(rec)

    ## TODO
    if len(recommendations) < 3:
        recommendations.append(recommendations[0])

    return recommendations
