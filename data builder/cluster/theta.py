import sys
sys.path.append('./data analyzer/location analyzer')
import DistanceCalculator
sys.path.append('./data analyzer/location analyzer/mapq')
import MapQuestAPI
sys.path.append('./data builder')
import database_getter

import math

CLOSE_LAT_LONG = 0.0041
MIN_VISITED_PLACE = 3
MIN_DOMINANT_TYPES_PERCENTAGE = 0.25
MIN_OVERLAP_TYPES = 2
MIN_EVENT_TYPE_PERCENTAGE = 0.75
MAX_DOMINANT_TYPES = 3
MAX_CLUSTER_RADIUS = 800

THETA = [-5e-4, 0.4, 1.11]

RATE_DICT = {
    67:'H',
    34:'M',
    0:'S'
}

RATE_RANK = {
    'HH':6,
    'HM':5,
    'HS':4,
    'MM':3,
    'MS':2,
    'SS':1
}

def _dist_func(dist):
    #the greater THETA[0] is, the more it penalizes far distance
    return THETA[0]*math.pow(dist,2) + 300

def _overlap_rate_func(r1, r2):
    #the greater THETA[1] is, the more rewarding higher rank is
    if r1*100 >= 67:
        r1_str = 'H'
    elif r1*100 >= 34:
        r1_str = 'M'
    else:
        r1_str = 'S'
    if r2*100 >= 67:
        r2_str = 'H'
    elif r2*100 >= 34:
        r2_str = 'M'
    else:
        r2_str = 'S'
    #print(r1_str+r2_str)
    try:
        return math.pow(2,math.exp(THETA[1])*RATE_RANK[r1_str+r2_str]) - 1
    except KeyError:
        return math.pow(2,math.exp(THETA[1])*RATE_RANK[r2_str+r1_str]) - 1

def _overlap_len_func(len):
    #the greater THETA[2] is, the more rewarding higher len is
    return math.pow(2,THETA[2]*len) - 1


def similarity(p1,p2):
    p1_name = p1[0]
    p1_address = p1[1]
    p1_types = [p for p in p1[2].split(',') \
        if not database_getter.is_in_address_type(p)]

    p2_name = p2[0]
    p2_address = p2[1]
    p2_types = [p for p in p2[2].split(',') \
        if not database_getter.is_in_address_type(p)]

    print(p1_types,p2_types)

    # dist = MapQuestAPI.get_distance_in_meters(p1_address,p2_address)
    # if dist < -100:
    dist = DistanceCalculator.get_distance(p1_address,p2_address)
    # if dist < 0:
    #     dist = 2500
    overlap_types = len(set(p1_types)&set(p2_types))
    #print(p1_types,p2_types,overlap_types)
    p1_overlap_rate = overlap_types/len(p1_types) if len(p1_types) else 0
    p2_overlap_rate = overlap_types/len(p2_types) if len(p2_types) else 0

    print(dist, overlap_types, p1_overlap_rate, p2_overlap_rate)
    # print(_dist_func(dist))
    # print(_overlap_rate_func(p1_overlap_rate,p2_overlap_rate))
    # print(_overlap_len_func(overlap_types))

    return _dist_func(dist) + _overlap_rate_func(p1_overlap_rate,\
        p2_overlap_rate) + _overlap_len_func(overlap_types)

#
#
# print(similarity(database_getter.get_location_info(\
#     "ChIJdTaxcwze3IARxzJAQZE9SeM"),database_getter.get_location_info(\
#     "ChIJj71SCQ3e3IARiltJQVzvYys")))
