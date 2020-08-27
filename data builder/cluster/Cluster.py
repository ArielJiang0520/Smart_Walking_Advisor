import math
import theta
import sys
sys.path.append('./')
import database_getter
from DataConnecter import Database
from collections import defaultdict

class Cluster:
    def __init__(self,uid):
        self.uid = uid
        self.members = set()
        self.center = (0,0)
        self.ave_dist_to_center = (0,0)
        self.dominant_types = []
        self._type_count = defaultdict(int)
        self.event_type = None
        self._event_count = defaultdict(int)
        self.frequency = 0
        self.ave_staying_time = 0

    def store_to_database(self,cid):
        d = Database()
        query = '''INSERT IGNORE INTO `cluster`(`uid`,`cid`,`members`,
`center_lat`,`center_long`,`ave_dist_to_center_lat`,`ave_dist_to_center_long`,
`dominant_types`,`ave_staying_time`,`frequency`,`event_type`)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''
        val = (self.uid, cid, ",".join(self.members), \
            self.center[0], self.center[1], self.ave_dist_to_center[0], self.ave_dist_to_center[1],
            ",".join(self.dominant_types), self.ave_staying_time, self.frequency, self.event_type)
        d.cursor.execute(query,val)
        d.db.commit()

    def __str__(self):
        members_str = ""
        for id in self.members:
            id_info = database_getter.get_location_info(self.uid, id)
            members_str+=f"{id_info[0]} {id_info[4]} {id_info[2]},{id_info[3]}\n"
        main_text = '''{}center: ({},{})
average distance to center: ({},{})
dominant types: {}
event type: {}
average staying time: {} min
cluster frequency: {}
        '''.format(members_str,\
        self.center[0],self.center[1],\
        self.ave_dist_to_center[0],self.ave_dist_to_center[1],\
        self.dominant_types,\
        self.event_type,\
        self.ave_staying_time, \
        self.frequency)
        return main_text

    def init_cluster(self,members):
        self.members = members
        self._init_center()
        self.update_ave_dist_to_center()
        self._init_frequency()
        self._init_dominant_types()
        self._init_ave_staying_time()
        self._init_event_type()

    def _init_event_type(self):
        for member in self.members:
            self.add_event(member)
        self.update_event_type()

    def add_event(self, place_id):
        associate_event = database_getter.get_location_info(self.uid, place_id)[7]
        self._event_count[associate_event]+=1

    def remove_event(self, place_id):
        associate_event = database_getter.get_location_info(self.uid, place_id)[7]
        self._event_count[associate_event]-=1

    def update_event_type(self):
        for k,v in sorted(self._event_count.items(), key=lambda x:x[1], reverse=True):
            if v >= math.ceil(theta.MIN_EVENT_TYPE_PERCENTAGE*len(self.members)):
                self.event_type = k

    def _init_ave_staying_time(self):
        for member in self.members:
            staying_time = database_getter.get_location_info(\
                self.uid,member)[5]
            self.ave_staying_time+=staying_time
        self.ave_staying_time/=len(self.members)

    def _init_frequency(self):
        for id in self.members:
            self.frequency += database_getter.get_location_info(self.uid, id)[6]

    def _init_center(self):
        total_lat = total_long = 0
        for id in self.members:
            id_info = database_getter.get_location_info(self.uid, id)
            lat,long = id_info[2], id_info[3]
            total_lat += lat
            total_long += long
        new_lat = total_lat/len(self.members)
        new_long = total_long/len(self.members)
        self.center = (new_lat,new_long)

    def _init_dominant_types(self):
        for id in self.members:
            self.add_types(id)
        self.update_dominant_types()

    def add_types(self,id):
        id_info = database_getter.get_location_info(self.uid, id)
        types = [t for t in id_info[4].split(',') \
            if not database_getter.is_in_address_type(t)]
        for t in types:
            self._type_count[t]+=1

    def remove_types(self,id):
        id_info = database_getter.get_location_info(self.uid, id)
        types = [t for t in id_info[4].split(',') \
            if not database_getter.is_in_address_type(t)]
        for t in types:
            self._type_count[t]-=1

    def update_dominant_types(self):
        result = []
        for k,v in sorted(self._type_count.items(),\
            key=lambda x:x[1], reverse=True):
            if v > math.ceil(theta.MIN_DOMINANT_TYPES_PERCENTAGE*len(self.members)):
                result.append(k)
        self.dominant_types = result[:theta.MAX_DOMINANT_TYPES]


    def accept_id(self,id_info):
        lat,long = id_info[2], id_info[3]
        types = [t for t in id_info[4].split(',') \
            if not database_getter.is_in_address_type(t)]
        associate_event = id_info[7]

        if self.event_type == 'school':
            if associate_event == self.event_type:
                print("event matched", self.event_type)
                return True

        if self.is_close_to_center(lat,long):
            if self.contain_types(types) >= theta.MIN_OVERLAP_TYPES:
                return True

        if self.contain_types(types) == theta.MAX_DOMINANT_TYPES:
            return True

        return False

    def is_close_to_center(self,lat,long):
        # print("lat diff:",math.fabs(lat-self.center[0]))
        # print("long diff:",math.fabs(long-self.center[1]))
        dist_lat_long = \
            math.fabs(math.fabs(lat - self.center[0]) - self.ave_dist_to_center[0]) + \
            math.fabs(math.fabs(long - self.center[1]) - self.ave_dist_to_center[1])
        #print(f"dist between average: {dist_lat_long}")
        return dist_lat_long < theta.CLOSE_LAT_LONG

    def contain_types(self,types):
        matched_types = 0
        for t in types:
            if t in self.dominant_types:
                matched_types+=1
        return matched_types

    def has_id(self,id):
        return id in self.members

    def add_member(self,id):
        self.frequency += database_getter.get_location_info(self.uid, id)[6]
        self.update_center_after_adding(id)
        self.update_staying_time_after_adding(id)
        self.members.add(id)
        self.update_ave_dist_to_center()
        self.add_types(id)
        self.update_dominant_types()
        self.add_event(id)
        self.update_event_type()

    def remove_member(self,id):
        self.frequency -= database_getter.get_location_info(self.uid, id)[6]
        self.update_center_after_removing(id)
        self.update_staying_time_after_removing(id)
        self.members.remove(id)
        self.update_ave_dist_to_center()
        self.remove_types(id)
        self.update_dominant_types()
        self.remove_event(id)
        self.update_event_type()

    def update_staying_time_after_removing(self,id):
        self.ave_staying_time = (self.ave_staying_time*len(self.members)-\
            database_getter.get_location_info(self.uid, id)[5])/(\
            len(self.members)-1)

    def update_staying_time_after_adding(self,id):
        self.ave_staying_time = (self.ave_staying_time*len(self.members)+\
            database_getter.get_location_info(self.uid, id)[5])/(\
            len(self.members)+1)

    def update_center_after_removing(self,id):
        id_info = database_getter.get_location_info(self.uid, id)
        lat,long = id_info[2], id_info[3]
        old_lat,old_long = self.center[0],self.center[1]
        new_lat = (len(self.members)*old_lat - lat)/(len(self.members) - 1)
        new_long = (len(self.members)*old_long - long)/(len(self.members) - 1)
        self.center = (new_lat,new_long)

    def update_center_after_adding(self,id):
        id_info = database_getter.get_location_info(self.uid, id)
        lat,long = id_info[2], id_info[3]
        old_lat,old_long = self.center[0],self.center[1]
        new_lat = (len(self.members)*old_lat + lat)/(len(self.members)+1)
        new_long = (len(self.members)*old_long + long)/(len(self.members)+1)
        self.center = (new_lat,new_long)

    def update_ave_dist_to_center(self):
        total_lat_dist_to_center = total_long_dist_to_center = 0
        for i in self.members:
            i_lat, i_long = database_getter.get_location_info(self.uid, i)[2],\
                database_getter.get_location_info(self.uid, i)[3]
            total_lat_dist_to_center += math.fabs(i_lat - self.center[0])
            total_long_dist_to_center += math.fabs(i_long - self.center[1])
        self.ave_dist_to_center = ((total_lat_dist_to_center/len(self.members)),\
            total_long_dist_to_center/len(self.members))

    def is_empty(self):
        return self.members == set()
