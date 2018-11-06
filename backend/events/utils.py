import os
from flask import current_app
import requests
import json
from backend.models import User, Event, Relationship, Expense

def get_address(address):
    endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    required_fields = "name,formatted_address,place_id,geometry/location"
    parameters = {'key': current_app.config['MAPS_API'],
                  'input': address,
                  'inputtype': 'textquery',
                  'fields': required_fields}
    raw_data = requests.get(url = endpoint, params = parameters)
    response = raw_data.json()
    return response['candidates'][0]['formatted_address']

def eventbrite_create_event(input_data, venue_id):
    token = current_app.config['EVENTBRITE_API']
    organization_id = current_app.config['ORGANIZATION_ID']
    organizer_id = current_app.config['ORGANIZER_ID']
    raw_data = json.loads(input_data)
    endpoint = 'https://www.eventbriteapi.com/v3/organizations/' + str(organization_id) + '/events/' + '?token=' + token
    headers = {'Content-type': 'application/json'}
    output_data = {
        'event': {
            'name': {
                'html': raw_data['name']
                },
            'description': {
                'html': raw_data['description']
                },
            'organizer_id': str(organizer_id),
            'start': {
                'utc': raw_data['startTime'],
                'timezone': "America/Chicago"
                },
            'end': {
                'utc': raw_data['endTime'],
                'timezone': "America/Chicago"
                },
            'currency': raw_data['currency'],
            'venue_id': venue_id,
            'online_event': raw_data['isOnline'],
            'listed': False,
            'capacity': raw_data['capacity'],
            'show_remaining': True
            }
        }
    output = requests.post(url = endpoint, json = output_data, headers = headers)
    return (str(output.json()['id']))
    
def eventbrite_ticket_class(event_id, input_data):
    token = current_app.config['EVENTBRITE_API']
    organization_id = current_app.config['ORGANIZATION_ID']
    organizer_id = current_app.config['ORGANIZER_ID']
    raw_data = json.loads(input_data)
    headers = {'Content-type': 'application/json'}
    endpoint = 'https://www.eventbriteapi.com/v3/events/' + str(event_id) + '/ticket_classes/' + '?token=' + token
    output_data = {
        'ticket_class': {
            'name': "RSVP",
            'quantity_total': raw_data['capacity'],
            'free': True,
            }
        }
    output = requests.post(url = endpoint, json = output_data, headers = headers)
    return None

def create_venue(name, place_id, organization_id):
    headers = {'Content-type': 'application/json'}
    endpoint = 'https://www.eventbriteapi.com/v3/organizations/' + str(organization_id) + '/venues' + '?' + 'token=' + current_app.config['EVENTBRITE_API']
    output_data = {
        'venue': {
            'name': name,
            'google_place_id': place_id
            }
        }
    output = requests.post(url = endpoint, json = output_data, headers = headers)
    return output.json()['venues'][0]['id']

def place_id_search(query):
    endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    required_fields = "name,formatted_address,place_id,geometry/location"
    parameters = {'key': current_app.config['MAPS_API'],
                  'input': query,
                  'inputtype': 'textquery',
                  'fields': required_fields}
##    request = endpoint + '?' + 'key=' + maps_key + '&' + 'input=' + input_string + 'inputtype=' + 'textquery'
##    response = requests.get(request)
    response = requests.get(url = endpoint, params = parameters)
    response_dict = response.json()
    return response_dict['candidates'][0]['place_id']

def eventbrite_create(input_data):
    location = (json.loads(input_data))['location']
    place_id = place_id_search(location)
    venue_id = create_venue(location, place_id, current_app.config['ORGANIZATION_ID'])
    eventbrite_id = eventbrite_create_event(input_data, venue_id)
    eventbrite_ticket_class(eventbrite_id, input_data)
    return eventbrite_id

def eventbrite_create_webhook(eventbrite_id):
	event_id = Event.query.filter_by(eventbrite_id = eventbrite_id).first().id
	endpoint = 'https://hackventure-emp.appspot.com/events/{event_id}/register'.format(event_id = event_id)
	actions = "order.placed"
	requests.post('https://www.eventbriteapi.com/v3/webhooks/?token={token}'.format(token = current_app.config['EVENTBRITE_API']), json = {'endpoint_url': endpoint, 'actions': actions, 'event_id': eventbrite_id, })

def test_caller():
    data = {
        'name': 'Test Event - Automatic',
        'description': 'Test Event - Automatic Description',
        'startTime': '2018-11-01T02:00:00Z',
        'endTime': '2018-11-02T02:00:00Z',
        'currency': 'USD',
        'isOnline': False,
        'capacity': 100
        }
