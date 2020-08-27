import googlemaps
import DistanceCalculator
import sys
sys.path.append('./')
import API

def get_place_types(place_id):
    gmaps = googlemaps.Client(key=API.KEY)
    detail_result = gmaps.place(place_id,fields=['type'])
    return detail_result['result']['types']

def get_place_address(place_id):
    gmaps = googlemaps.Client(key=API.KEY)
    detail_result = gmaps.place(place_id,fields=['formatted_address'])
    return detail_result['result']['formatted_address']

def get_guess_info_from_id(place_id):
    text_address = get_place_address(place_id) + " guess"
    gmaps = googlemaps.Client(key=API.KEY)
    detail_result = gmaps.find_place(input=text_address, input_type='textquery',\
                        fields=['name','formatted_address','types'])
    try:
        return detail_result['candidates'][0]
    except IndexError:
        return {'name':None,'formatted_address':None,'types':[]}
    #return detail_result['name'],detail_result['formatted_address'],detail_result['types'],

# TODO: add open now
def get_nearby_places(location, keyword=None, radius=None, \
    rank_by=None, exclude_kw=[]):
    gmaps = googlemaps.Client(key=API.KEY)
    try:
        nearby_list = gmaps.places_nearby(location=location, radius=radius,\
            rank_by=rank_by, keyword=keyword) #open_now
    except googlemaps.exceptions.ApiError:
        return []
    return_list = []
    for result in nearby_list["results"]:
        if not (set(exclude_kw) & set(result['types'])):
            name = result['name']
            lat, long = result["geometry"]["location"]["lat"], \
                result["geometry"]["location"]["lng"]
            place_id = result['place_id']
            address = result['vicinity']
            types = result['types']
            return_list.append((name, place_id, address, (lat,long), types))
    return return_list

##print(get_place_address('ChIJIeXl0wze3IAR5YKtYx7cO0c'))
#print(get_place_name_from_text('4541 Campus Dr guess'))
#print(get_place_name_and_address('4225 Campus Dr guess'))
# print(get_place_types('ChIJIeXl0wze3IAR5YKtYx7cO0c'))
# print(get_place_types('ChIJzW3cvA_e3IARM3dvomowDEc'))
# print(get_place_types('ChIJuZ4dHhLe3IARykBwRywlcuQ'))
# for i in get_nearby_places((33.6498, -117.839), keyword='food', rank_by='distance'):
#     print(i)
#https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=4545%20Campus%20Dr,%20Irvine%20guess&inputtype=textquery&fields=formatted_address,name,types&key=AIzaSyBxEEVz68DNtTWphXz6lUDM7g822VLMt3o
#https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=33.7253310,-117.9873913&radius=1500&type=restaurant&key=AIzaSyBxEEVz68DNtTWphXz6lUDM7g822VLMt3o
