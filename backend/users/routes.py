from flask import current_app, Blueprint, request
from backend.models import User, Event, Relationship
from backend import db, bcrypt
import requests
import json
from backend.users.utils import get_ind_savings

users = Blueprint('users', __name__)

@users.route('/login', methods = ['GET', 'POST'])
def login():
	request_json = request.get_json()
	email = request_json['email']
	password = request_json['password']
	user = User.query.filter_by(email = email).first()
	if user and bcrypt.check_password_hash(user.password, password):
		final_dict = {
			'id': user.id,
			'auth_token': user.get_auth_token(),
			'name': user.name,
			'email': user.email,
			'isAdmin': user.isAdmin,
			'validator': True
		}
		return json.dumps(final_dict)
	else:
		final_dict = {
			'validator': False
		}
		return json.dumps(final_dict)

@users.route('/register', methods = ['GET', 'POST'])
def register():
	request_json = request.get_json()
	if User.query.filter_by(email = request_json['email']).first():
		return json.dumps({'status': 0, 'output': User.query.filter_by(email = request_json['email']).first().email})
	email = request_json['email']
	hashed_pwd = bcrypt.generate_password_hash(request_json['password']).decode('utf-8')
	name = request_json['name']
	meal_pref = request_json['meal_pref']
	user = User(email = email, password = hashed_pwd, name = name, meal_pref = meal_pref)
	db.session.add(user)
	db.session.commit()
	return json.dumps({'id': user.id, 'status': 1})

@users.route('/users/events', methods = ['GET', 'POST'])
def grab_events():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({'status': 0})
	else:
		relationships = Relationship.query.filter_by(user_id = user.id)
		response_list = []
		for relationship in relationships:
			event = Event.query.filter_by(id = relationship.event_id).first()
			response_list.append({"id": event.id, "name": event.name, "date": str(event.date), "description": event.description, "address": event.address, "mini_address": event.mini_address})
		return json.dumps({"rows": response_list})

@users.route('/users/all', methods = ['GET', 'POST'])
def get_all_users():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({'status': 0})
	else:
		response_list = []
		users = User.query.all()
		for user in users:
			response_list.append({"id": user.id, "name": user.name, "email": user.email, "isAdmin": bool(user.isAdmin)})
		return json.dumps({"rows": response_list})

@users.route('/users/dashboard', methods = ['GET', 'POST'])
def get_user_stats():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({'status': 0})
	else:
		response_list = []
		events = Event.query.all()
		response_list.append({'name': 'Events', 'value': str(len(events))})
		response_list.append({'name': 'Upcoming Events', 'value': str(len(events))})
		users = User.query.all()
		response_list.append({'name': 'Users', 'value': str(len(users))})
		relationships = Relationship.query.all()
		response_list.append({'name': 'Registrations', 'value': str(len(relationships))})
		response_list.append({'name': 'Avg Registrations per user', 'value': str(round(len(relationships)/len(users), 2))})
		saving = 0
		allocated = 0
		for event in events:
			saved = get_ind_savings(event.id)
			if saved > 0:
				saving += saved
			allocated += event.allocated_budget
		response_list.append({'name': 'Total Saved', 'value': '$' + str(saving)})
		response_list.append({'name': 'Avg Saved per event', 'value': '$' + str(round(saving/len(events), 2))})
		response_list.append({'name': 'Total Allocated', 'value': '$' + str(allocated)})
		response_list.append({'name': 'Total Available to Spend', 'value': '$' + str(saving)})
		return json.dumps({'stats': response_list})
		
		
		

@users.route('/test', methods = ['GET'])
def test():
	return "Hello World"