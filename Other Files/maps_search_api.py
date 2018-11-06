'''
This module deals with Google Maps Place Search API.
The required input is the string provided by the user
to make the search. Once provided, the outputs provided
include:
['candidates'][0]['formatted_address']
['candidates'][0]['geometry']['location']['lat']
['candidates'][0]['geometry']['location']['lng']
['candidates'][0]['name']
['candidates'][0]['place_id']
'''

import json
import requests
import urllib
import urllib3

maps_key = 'AIzaSyAs5sA8X7MR-vbuNNxfJ4a-xSiUeOLtg-U'

def caller(input_string):
    endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    required_fields = "name,formatted_address,place_id,geometry/location"
    parameters = {'key': maps_key,
                  'input': input_string,
                  'inputtype': 'textquery',
                  'fields': required_fields}
##    request = endpoint + '?' + 'key=' + maps_key + '&' + 'input=' + input_string + 'inputtype=' + 'textquery'
##    response = requests.get(request)
    response = requests.get(url = endpoint, params = parameters)
    print(response.text)
    response_dict = response.json()
    return response_dict
