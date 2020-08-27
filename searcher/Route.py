import sys
sys.path.append('./scorer')
import scorer
sys.path.append('./data builder')
import cluster_getter
sys.path.append('./data analyzer/location analyzer')
import DistanceCalculator, YelpAPI

class Route:
    def __init__(self, stop, origin, dest, mode='walking'):
        assert len(stop) == 5, "stop attribute is not a list w/ 5 elements"
        self.origin = origin #lat,long
        self.dest = dest #address
        self.score = 0
        self.mode = mode

        self.stop_name = stop[0]
        self.stop_id = stop[1]
        self.stop_address = stop[2]
        self.stop_lat = stop[3][0]
        self.stop_long = stop[3][1]
        self.stop_types = stop[4] + YelpAPI.get_categories_from_name_and_address(
            name=self.stop_name,address=self.stop_address)

        self.origin_to_stop = DistanceCalculator.get_distance_and_time(\
            self.origin,self.stop_address)
        self.stop_to_dest = DistanceCalculator.get_distance_and_time(\
            self.stop_address,self.dest) \
            if self.dest != None else (0,0) #meter seconds

        self.step_to_stop = round(DistanceCalculator.meter_to_mile(\
            self.origin_to_stop[0])*2000)
        self.step_to_dest = round(DistanceCalculator.meter_to_mile(\
            self.stop_to_dest[0])*2000)

        if mode == 'driving':
            if self.origin_to_stop[1] > self.stop_to_dest[1]:
                self.origin_to_stop = DistanceCalculator.get_distance_and_time(\
                    self.origin,self.dest,'driving')
                self.origin_to_stop = (0,self.origin_to_stop[1])
                self.step_to_stop = 0

            else:
                self.stop_to_dest = DistanceCalculator.get_distance_and_time(\
                    self.origin,self.dest,'driving')
                self.stop_to_dest = (0,self.stop_to_dest[1])
                self.step_to_dest = 0

        self.trip_time = round((
            self.origin_to_stop[1]+self.stop_to_dest[1])/60) #min
        self.total_dist = self.origin_to_stop[0]+self.stop_to_dest[0]

    def set_staying_time(self,uid):
        cid = cluster_getter.get_cid(
            uid,self.stop_id,self.stop_lat,self.stop_long,self.stop_types)
        if cid:
            self.staying_time = cluster_getter.get_staying_time(uid,cid)
        else:
            self.staying_time = scorer.DEFAULT_STAYING_TIME
        self.total_time = self.trip_time + self.staying_time

    def add_score(self,score):
        self.score += score
