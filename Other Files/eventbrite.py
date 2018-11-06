import json
import requests
import urllib
import urllib3

'''
This function creates an event.

The required inputs include:
Event Name:        ['name']
Event Description: ['description']
Event Start Time:  ['startTime']
Event End Time:    ['endTime']
Event Currency:    ['currency'] --> Use USD always, for now
Event OnlineStatus:['isOnline']
Event Capacity:    ['capacity']

The outputs of this function include the data returned
by the EventBrite API.
'''

def eventbrite_create(input_data):
    file_data = open('eventbrite_data.json', 'r')
    organization_data = json.load(file_data)
    token = organization_data['token']
    organization_id = organization_data['rows'][0]['organization_id']
    organizer_id = organization_data['rows'][0]['organizers'][0]['id']
    raw_data = json.loads(input_data)
    endpoint = 'https://www.eventbriteapi.com/v3/organizations/' + str(organization_id) + '/events/' + '?token=' + token
    print(token)
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
                'timezone': "America/New_York"
                },
            'end': {
                'utc': raw_data['endTime'],
                'timezone': "America/New_York"
                },
            'currency': raw_data['currency'],
            'online_event': raw_data['isOnline'],
            'listed': False,
            'capacity': raw_data['capacity'],
            'show_remaining': True
            }
        }
    output = requests.post(url = endpoint, json = output_data, headers = headers)
    file_data.close()
    return json.load(output)

def eventbrite_ticket_class(event_id, input_data):
    file_data = open('eventbrite_data.json', 'r')
    organization_data = json.load(file_data)
    token = organization_data['token']
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
    file_data.close()
    return json.load(output)

def create_venue(name, place_id, organization_id):
    headers = {'Content-type': 'application/json'}
    endpoint = 'https://www.eventbriteapi.com/v3/organizations/' + str(organization_id) + '/venues/'
    output_data = {
        'venue': {
            'name': name,
            'google_place_id': place_id
            }
        }
    output = requests.post(url = endpoint, json = output_data, headers = headers)
    return json.load(output)

def test_caller():
    data = {
        'name': 'Test Event - Automatic',
        'description': 'Test Event - Automatic Description',
        'startTime': '2018-11-01T02:00:00Z',
        'endTime': '2018-11-02T02:00:00Z',
        'currency': 'USD',
        'isOnline': False,
        'capacity': 20
        }
##    eventbrite_create(json.dumps(data))
    event_id = 51947155340
    eventbrite_ticket_class(event_id, json.dumps(data))
