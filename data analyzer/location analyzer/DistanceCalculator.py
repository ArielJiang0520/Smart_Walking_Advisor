import googlemaps
import Geocoding
import sys
sys.path.append('./')
import API

def meter_to_mile(meter):
    return meter*0.000621371

def mile_to_meter(mile):
    return mile/0.000621371

def mile_to_steps(mile):
    return int(mile*2000)

def steps_to_mile(steps):
    return steps/2000

def get_distance(origin, dest):
    assert type(origin) is not list
    assert type(dest) is not list
    gmaps = googlemaps.Client(key=API.KEY)
    matrix = gmaps.distance_matrix(origins = origin, destinations = dest,\
                            mode="walking",units="imperial")
    try:
        return matrix["rows"][0]["elements"][0]["distance"]["value"]
    except KeyError:
        return -1

def get_distance_and_time(origin,dest,mode='walking'):
    assert type(origin) is not list
    assert type(dest) is not list
    gmaps = googlemaps.Client(key=API.KEY)
    matrix = gmaps.distance_matrix(origins = origin, destinations=dest,\
                                    mode=mode,units="imperial")
    try:
        return matrix["rows"][0]["elements"][0]["distance"]["value"],\
            matrix["rows"][0]["elements"][0]["duration"]["value"]
    except KeyError:
        return -1,-1

#print(get_distance_and_time((33.6503829,-117.8390142),  "8876 Warner Ave #3200\nFountain Valley, CA 92708\nUSA"))

def get_distance_and_time_matrix(origins,destinations):
    gmaps = googlemaps.Client(key=API.KEY)
    matrix = gmaps.distance_matrix(origins = origins, destinations=destinations,\
                                    mode="walking",units="imperial")
    return matrix

def matrix_to_origin_dict(matrix):
    origin_dict = dict()
    #print(matrix)
    dest_list = matrix["destination_addresses"]
    #dest_id_list = [Geocoding.get_id(d) for d in dest_list]
    for n,info in enumerate(matrix["rows"][0]["elements"]):
        origin_dict[dest_list[n]] = (info["distance"]["value"], info["duration"]["value"])
    #print(origin_dict)
    return origin_dict

def matrix_to_dest_dict(matrix):
    dest_dict = dict()
    origin_list = matrix["origin_addresses"]
    #origin_id_list = [Geocoding.get_id(o) for o in origin_list]
    for n,info in enumerate(matrix["rows"]):
        dest_dict[origin_list[n]] = (info["elements"][0]["distance"]["value"],info["elements"][0]["duration"]["value"])
    #print(dest_dict)
    return dest_dict

#print(get_distance("758 Stanford Ct\nIrvine, CA 92612\nUSA", "8876 Warner Ave #3200\nFountain Valley, CA 92708\nUSA"))

# m = get_distance_and_time((33.6503829,-117.8390142),[(33.6532819,-117.8395018),(33.6432551,-117.8420085)])
# n = get_distance_and_time([(33.6532819,-117.8395018),(33.6432551,-117.8420085)],(33.6503829,-117.8390142))
# matrix_to_origin_dict(m)
# matrix_to_dest_dict(n)
