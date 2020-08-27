from yelpapi import YelpAPI

yelp_api = YelpAPI(MY_API_KEY)

def get_alias_from_name_and_address(name,address):
    yelp_api = YelpAPI(MY_API_KEY)
    result = yelp_api.search_query(term=name, location=address,sort_by='best_match', limit=1)
    try:
        return result['businesses'][0]['alias']
    except IndexError:
        return ""

def get_categories_from_name_and_address(name,address):
    yelp_api = YelpAPI(MY_API_KEY)
    alias = get_alias_from_name_and_address(name,address)
    if alias == "":
        return []
    else:
        result = yelp_api.business_query(id=alias)
        return [ c['alias'] for c in result['categories'] ]
