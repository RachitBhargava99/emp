from flask import current_app, Blueprint, request, url_for
from backend.models import Event, User, Relationship
from backend import db, bcrypt
import requests
import json
from backend.events.utils import get_address, eventbrite_create, eventbrite_create_webhook

events = Blueprint('events', __name__)

@events.route('/events/create', methods = ['GET', 'POST'])
def create_event():
##	try:
	request_json = request.get_json()
	name = request_json['name']
	date_data = request_json['date']
	date = '{year}-{month}-{day} {hour}:{minute}:00'.format(year = date_data[0], month = date_data[1], day = date_data[2], hour = date_data[3], minute = date_data[4])
	description = request_json['description']
	address = request_json['address']
	veg_price = float(request_json['veggie'])
	nvg_price = float(request_json['nonveg'])
	vgn_price = float(request_json['veganp'])
	allocated_budget = float(request_json['allocated_funds'])
	eventbrite_input = {'name': name, 'description': description, 'startTime': '{year}-{month}-{day}T{hour}:{minute}:00Z'.format(year = date_data[0], month = date_data[1], day = date_data[2], hour = date_data[3], minute = date_data[4]), 'endTime': '2019-12-31T11:59:59Z', 'currency': 'USD', 'isOnline': False, 'capacity': 100, 'location': address}
	eventbrite_id = eventbrite_create(json.dumps(eventbrite_input))
	event = Event(name = name, date = date, description = description, address = get_address(address), mini_address = address, veg_price = veg_price, non_veg_price = nvg_price, vegan_price = vgn_price, allocated_budget = allocated_budget, eventbrite_id = eventbrite_id)
	db.session.add(event)
	db.session.commit()
	eventbrite_create_webhook(eventbrite_id)
	return json.dumps({'status': 1, 'event_id': event.id})
##	except Exception as e:
##		return json.dumps({'status': 0, 'error': str(e)})

@events.route('/events/all', methods = ['GET', 'POST'])
def return_all_events():
	final_dict = {"rows": []}
	for event in Event.query.all():
		final_dict['rows'].append({
				"id": event.id,
				"name": event.name,
				"date": str(event.date),
				"description": event.description,
				"address": event.address,
				"mini_address": event.mini_address
			}
		)
	return json.dumps(final_dict)

@events.route('/events/<int:event_id>', methods = ['GET', 'POST'])
def return_event_info(event_id):
	final_dict = {"rows: []"}
	event = Event.query.filter_by(event_id = event.id)
	final_dict['rows'].append({
			"id": event.id,
			"name": event.name,
			"date": str(event.date),
			"description": event.description,
			"address": event.address,
			"mini_address": event.mini_address
		}
	)
	return json.dumps(final_dict)


@events.route('/events/<int:event_id>/register', methods = ['GET', 'POST'])
def user_event_register(event_id):
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({'status': 0})
	else:
		relationships = Relationship.query.filter_by(user_id = user.id)
		for relationship in relationships:
			if event_id == relationship.event_id:
				return json.dumps({'status': 2})
		rel = Relationship(user_id = user.id, event_id = event_id)
		db.session.add(rel)
		db.session.commit()
		return json.dumps({'status': 1})

@events.route('/events/<int:event_id>/register/<int:eventbrite_id>', methods = ['GET', 'POST'])
def user_event_register_eventbrite(event_id, eventbrite_id):
	last_attendee = requests.get('https://www.eventbriteapi.com/v3/events/{eventbrite_id}/attendees/'.format(eventbrite_id = event_id)).json()['attendees'][-1]['profile']
	name = last_attendee['name']
	email = last_attendee['email']
	user_id = requests.post(url_for('backend.users.routes.register'), json = json.dumps({'email': email, 'password': 'password', 'name': name, 'meal_pref': 0}))
	rel = Relationship(user_id = user_id, event_id = event_id)
	db.session.add(rel)
	db.session.commit()
	return json.dumps({'status': 1})

@events.route('/events/<int:event_id>/attendees', methods = ['GET', 'POST'])
def get_user_list(event_id):
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({'status': 0})
	else:
		relationships = Relationship.query.filter_by(event_id = event_id)
		response_list = []
		for relationship in relationships:
			user_p = User.query.filter_by(id = relationship.user_id).first()
			response_list.append({'id': user_p.id, 'name': user_p.name, 'email': user_p.email, 'meal_pref': user_p.meal_pref})
		return json.dumps({"rows": response_list})

@events.route('/events/<int:event_id>/remaining_amount', methods = ['GET', 'POST'])
def get_savings(event_id):
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({'status': 0})
	else:
		users = routes.get_user_list(event_id)['rows']
		veg, nonveg, vegan = meal_div(users)
		
		event = Event.query.filter_by(event_id = event_id).first()
		expense0 = veg * event.veg_price
		expense1 = nonveg * event.non_veg_price
		expense2 = vegan * event.vegan_price
		final_expense = expense0 + expense1 + expense2

		cost0 = {'expense': final_expense}
		response_list = []
		expenses = Expense.query.filter_by(event_id = event_id)
		for expense in expenses:
			response_list.append({"name": expense.name, "value": expense.value})
		
		cost1 = response_list
		costs = {"rows": [{"name": "Meals", "value": cost0['expense']}] + cost1}
		
		other_costs = 0
		meal = 0
		for cost in costs['rows']:
			if cost['name'] == "Meals":
				meal = cost['value']
			else:
				other_costs += cost['value']
		total = other_costs + meal
		
		event = Event.query.filter_by(event_id = event_id)
		remaining_amount = event.allocated_funds - total
		return json.dumps({"remaining_amount": remaining_amount, "status": 1})