import math
import sys
sys.path.append('./data builder')
import database_getter

GOOD_EVENT_TYPE_SCORE = 3.5
SEVERE_PENALTY = -1e9


K_RESULTS = 3
DISTANCE_REGULARIZED = 0.7
MIN_STAYING_TIME = 5
MAX_EVENT_GAP = 120

MAX_SPARE_TIME = 60

SHORT_STOP_TYPES = {'bakery','tea'}
LONG_STOP_TYPES =  {'library'}

BAD_EVENT_BIAS = {'home','school','work'}

DEFAULT_STAYING_TIME = 25

PAST_LOCATION_BONUS = 5

POSITIVE_SURPLUS_BONUS = 10

def normalize(a,b,d):
    return (a*d)/b

def logistic(L,a,b,c,x):
    return (L/(1+math.exp(-a*(x+b))))+c

def goal_distance_func(ideal_distance, route_distance):
    # print(ideal_distance,route_distance)
    diff = math.fabs(ideal_distance-route_distance)/1000
    # print("diff",diff)
    # print("logistic",logistic(L=-1,a=1.5,b=0,c=1,x=diff))
    return normalize(logistic(L=-1,a=1.5,b=0,c=1,x=diff),0.5,10)

#print(goal_distance_func(1609,2394))

def past_location_func(is_past_location):
    if is_past_location:
        return PAST_LOCATION_BONUS
    else:
        return 0

def staying_time_func(surplus, staying_time):
    if surplus >= 0:
        #positive surplus
        return POSITIVE_SURPLUS_BONUS
    else:
        #negative surplus
        ratio = -1*surplus/staying_time
        return 10 - normalize(logistic(
            L=-1,a=7,b=-0.5,c=0,x=ratio),-1,10)

def event_bias_func(bias,types):
    score = 0
    for b in bias:
        if set(types) & set(database_getter.EVENT_TYPES[b]):
            score+=GOOD_EVENT_TYPE_SCORE
    return score
