from RouteService import RouteService
import sys
sys.path.append('./data analyzer/location analyzer')
import DistanceCalculator

def get_distance_in_meters(origin,dest):
    service = RouteService('L3A9uBQK7tdij6aU6trWi8etutLyBNXl')
    location_list = [origin,dest]
    routeMatrix = service.routeMatrix(locations=location_list)
    try:
        return DistanceCalculator.mile_to_meter(routeMatrix['distance'][1]*1.3)
    except KeyError:
        return -1e9
#
# print(get_distance_in_meters('4255 Campus Dr A150 Irvine, CA 92612 USA',\
#     '4225 Campus Dr Irvine, CA 92612 USA'))
