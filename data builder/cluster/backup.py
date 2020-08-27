import math
import theta
import sys
sys.path.append('./')
import database_getter
from collections import defaultdict

class Cluster:
    def __init__(self,uid):
        self.uid = uid
        self.members = set()
        self.center = (0,0)
        self.ave_dist_to_center = (0,0)
        self.dominant_types = []
        self._type_count = defaultdict(int)
        self.frequency = 0
        self.ave_staying_time = 0

    @staticmethod
    def accept_id(cluster_info,id_info):
        lat,long = id_info[2], id_info[3]
        types = types = [t for t in id_info[4].split(',') \
            if not database_getter.is_in_address_type(t)]
        staying_time = id_info[5]
        cluster_lat, cluster_long = cluster_info[3],[4]
        cluster_lat_to_center, cluster_long_to_center = \
            cluster_info[5],cluster_info[6]
        cluster_types = cluster_info[7]
        cluster_ave_staying_time = cluster_info[8]

        if Cluster.is_close_to_center(lat,long,cluster_lat,cluster_long,\
            cluster_lat_to_center,cluster_long_to_center):
            if Cluster.contain_types(types,cluster_types):
                if math.fabs(cluster_ave_staying_time - staying_time) \
                    < theta.MIN_STAYING_TIME_DIFF:
                    return True
        return False

    def __str__(self):
        members_str = ""
        for id in self.members:
            id_info = database_getter.get_location_info(id)
            members_str+=f"{id_info[0]} {id_info[4]} {id_info[2]},{id_info[3]}\n"
        main_text = '''{}center: ({},{})
average distance to center: ({},{})
dominant types: {}
average staying time: {} min
cluster frequency: {}
        '''.format(members_str,self.distance_to_home,\
        self.distance_to_school,\
        self.center[0],self.center[1],\
        self.ave_dist_to_center[0],self.ave_dist_to_center[1],\
        self.dominant_types,\
        self.ave_staying_time, self.frequency)
        return main_text

    def init_cluster(self,members):
        self.members = members
        self._init_center()
        self.update_ave_dist_to_center()
        self._init_frequency()
        self._init_dominant_types()
        self._init_ave_staying_time()

    def _init_ave_staying_time(self):
        for member in self.members:
            staying_time = database_getter.get_location_info(\
                self.uid,member)[5]
            self.ave_staying_time+=staying_time
        self.ave_staying_time/=len(self.members)

    def _init_frequency(self):
        for id in self.members:
            self.frequency += database_getter.get_total_location_frequency(id)

    def _init_center(self):
        total_lat = total_long = 0
        for id in self.members:
            id_info = database_getter.get_location_info(id)
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
        id_info = database_getter.get_location_info(id)
        types = [t for t in id_info[4].split(',') \
            if not database_getter.is_in_address_type(t)]
        for t in types:
            self._type_count[t]+=1

    def update_dominant_types(self):
        result = []
        for k,v in sorted(self._type_count.items(),\
            key=lambda x:x[1], reverse=True)[:theta.MAX_DOMINANT_TYPES]:
            if v > math.ceil(theta.MIN_DOMINANT_TYPES_PERCENTAGE*len(self.members)):
                result.append(k)
        self.dominant_types = result


    @staticmethod
    def is_close_to_center(lat,long,self_lat,self_long,\
        self_lat_to_center,self_long_to_center):
        # print("lat diff:",math.fabs(lat-self.center[0]))
        # print("long diff:",math.fabs(long-self.center[1]))
        dist_lat_long = math.fabs(math.fabs(lat-self_lat) - \
            self_lat_to_center) + \
            math.fabs(math.fabs(long-self_long) - \
            self_long_to_center)
        # print(f"dist between average: {dist_lat_long}")
        return dist_lat_long < theta.CLOSE_LAT_LONG

    @staticmethod
    def contain_types(types,cluster_types):
        matched_types = 0
        for t in types:
            if t in cluster_types:
                matched_types+=1
        return matched_types

    def has_id(self,id):
        return id in self.members

    def add_member(self,id):
        self.frequency += database_getter.get_total_location_frequency(id)
        self.update_center_after_adding(id)
        self.members.add(id)
        self.update_ave_dist_to_center()
        self.add_types(id)
        self.update_dominant_types()

    @staticmethod
    def update_center_after_adding(place_id, old_lat, old_long, ):
        id_info = database_getter.get_location_info(id)
        lat,long = id_info[2], id_info[3]
        old_lat,old_long = self.center[0],self.center[1]
        new_lat = (len(self.members)*old_lat + lat)/(len(self.members)+1)
        new_long = (len(self.members)*old_long + long)/(len(self.members)+1)
        return new_lat,new_long

    def update_ave_dist_to_center(self):
        total_lat_dist_to_center = total_long_dist_to_center = 0
        for i in self.members:
            i_lat, i_long = database_getter.get_location_info(i)[2],\
                database_getter.get_location_info(i)[3]
            total_lat_dist_to_center += math.fabs(i_lat - self.center[0])
            total_long_dist_to_center += math.fabs(i_long - self.center[1])
        self.ave_dist_to_center = ((total_lat_dist_to_center/len(self.members)),\
            total_long_dist_to_center/len(self.members))

    def is_empty(self):
        return self.members == set()
