import sys
sys.path.append('./')
from DataConnecter import Database
import datetime

RECOMMENDATION_TYPES = {\
    0:'calendar_based',\
    1:'habit_based',\
    2:'friend_based'}

RECOMMENDATION_RESULT = {\
    0:'unfinished',
    1:'bad',
    2:'neutral',
    3:'good'}

RECOMMENDATION_FEEDBACK = {\
    0:'It\'s okay. Not too bad or too good',
    1:'The walk is too long',
    2:'I don\'t like the destination',
    3:'The timing is too tight for my schedule',
    4:'I\'ve been to that place too many times',
    5:'I don\'t feel like walking right now',
    6:'The destination is random and irrelevant to me'}

class Recommendation:
    def __init__(self, uid, type, \
        start_time, duration, \
        place_id, place_name, place_address,
        place_types, steps, report):
        self.uid = uid
        self.type = type
        self.start_time = start_time
        self.duration = duration
        self.place_id = place_id
        self.place_name = place_name
        self.place_address = place_address
        self.place_types = place_types
        self.steps = steps

        self.result = RECOMMENDATION_RESULT[0]
        self.feedback = []

        self.arrival_time = (self.start_time \
            + datetime.timedelta(seconds=self.duration)).strftime("%m/%d, %H:%M")

        self.report = report

    @staticmethod
    def add_to_db(r):
        d = Database()
        query = '''INSERT IGNORE INTO `recommendation`(
        uid,type,start_time,duration,place_id,place_name,
        place_address,place_types,steps)
        VALUES ("{0}", {1}, "{2}", {3}, "{4}", "{5}", "{6}", "{7}", {8})
        '''.format(r.uid, r.type, r.start_time, r.duration,\
        r.place_id, r.place_name, r.place_address, \
        ",".join(r.place_types), r.steps)
        d.cursor.execute(query)
        d.db.commit()

    def finish_recommendation(self, result, feedback=[]):
        self.result = RECOMMENDATION_RESULT[result]
        self.feedback = feedback
