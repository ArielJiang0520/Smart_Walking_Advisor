import googlemaps
import sys
sys.path.append('./')
import API

def get_geocode(address):
    gmaps = googlemaps.Client(key=API.KEY)
    geocode_result = gmaps.geocode(address)
    #print(geocode_result)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    long = geocode_result[0]["geometry"]["location"]["lng"]
    return lat,long

def get_id_from_address(address):
    gmaps = googlemaps.Client(key=API.KEY)
    geocode_result = gmaps.geocode(address)
    return geocode_result[0]["place_id"]

#print(get_id_from_address("930 Roosevelt, Irvine, CA 92620"))
def get_id_from_geocode(geocode):
    gmaps = googlemaps.Client(key=API.KEY)
    reverse_geocode_result = gmaps.reverse_geocode(geocode)
    return get_id_from_address(\
        reverse_geocode_result[0]["formatted_address"])

def get_address(geocode):
    gmaps = googlemaps.Client(key=API.KEY)
    reverse_geocode_result = gmaps.reverse_geocode(geocode)
    return reverse_geocode_result[0]["formatted_address"]

#print(get_id("758 Stanford Ct\nIrvine, CA 92612\nUSA"))
# print(get_address((33.7253310,-117.9873913)))
