from flask import current_app, Blueprint, request, url_for
from backend.models import Event, User, Relationship, Expense
from backend import db, bcrypt
import requests
import json
from backend.events import routes
from backend.finance.utils import meal_div_users as meal_div
from backend.finance.utils import get_ind_savings

finance = Blueprint('finance', __name__)

@finance.route('/finance/expense/meals', methods = ['GET', 'POST'])
def meals_costs():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	event_id = request_json['event_id']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({"status": 0})
	else:
		users = (json.loads(routes.get_user_list(event_id)))['rows']
		veg, nonveg, vegan = meal_div(users)
		event = Event.query.filter_by(id = event_id).first()
		expense0 = veg * event.veg_price
		expense1 = nonveg * event.non_veg_price
		expense2 = vegan * event.vegan_price
		final_expense = expense0 + expense1 + expense2
		return json.dumps({"expense": final_expense, "status": 1})

@finance.route('/finance/expense/add', methods = ['GET', 'POST'])
def add_expense():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({"status": 0})
	else:
		event_id = request_json['event_id']
		name = request_json['name']
		value = request_json['price']
		expense = Expense(name = name, value = value, event_id = event_id)
		db.session.add(expense)
		db.session.commit()
		return json.dumps({"status": 1})

@finance.route('/finance/expense/others', methods = ['GET', 'POST'])
def other_costs():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	event_id = request_json['event_id']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({"status": 0})
	else:
		response_list = []
		expenses = Expense.query.filter_by(event_id = event_id)
		for expense in expenses:
			response_list.append({"name": expense.name, "value": expense.value})
		return json.dump({"rows": []})

@finance.route('/finance/expense/view', methods = ['GET', 'POST'])
def view_costs():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	event_id = request_json['event_id']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({"status": 0})
	else:
		users = (json.loads(routes.get_user_list(event_id)))['rows']
		veg, nonveg, vegan = meal_div(users)
		
		event = Event.query.filter_by(id = event_id).first()
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
		final_costs = {"rows": [{"name": "Meals", "value": cost0['expense']}] + cost1}
		return json.dumps(final_costs)

@finance.route('/finance/expense/summary', methods = ['GET', 'POST'])
def summary_costs():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({"status": 0})
	else:
		users = (json.loads(routes.get_user_list(event_id)))['rows']
		veg, nonveg, vegan = meal_div(users)
		
		event = Event.query.filter_by(id = event_id).first()
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
		
		event = Event.query.filter_by(id = event_id)
		remaining_amount = event.allocated_budget - total
		return json.dumps({'meal': meal, 'other': other_costs, 'total': total, 'status': 1})

@finance.route('/finance/manager', methods = ['GET', 'POST'])
def finance_manager():
	request_json = request.get_json()
	auth_token = request_json['auth_token']
	user = User.verify_auth_token(auth_token)
	if not user:
		return json.dumps({"status": 0})
	else:
		manager_code = request_json['manager_code']
		if manager_code == 0:
			'''View Expenses'''
			event_id = request_json['event_id']
			users = (json.loads(routes.get_user_list(event_id)))['rows']
			veg, nonveg, vegan = meal_div(users)
			
			event = Event.query.filter_by(id = event_id).first()
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
			
			event = Event.query.filter_by(id = event_id).first()
			remaining_amount = event.allocated_budget - total
		return json.dumps({"rows": [{'name': 'Meal Costs', 'value': '$' + str(meal)}, {'name': 'Other Costs', 'value': '$' + str(other_costs)}, {'name': 'Total Expenditure', 'value': '$' + str(total)}, {'name': 'Remaining Amount', 'value': '$' + str(remaining_amount)}]})

@finance.route('/finance/stack_stats', methods = ['GET', 'POST'])
def stack_stats():
	events = Event.query.all()
	response_list = []
	for event in events:
		saved = get_ind_savings(event.id)
		if saved < 0:
			spend = 1
			save = 0
		elif event.allocated_budget == 0:
			save = 0.5
			spend = 0.5
		else:
			budget = event.allocated_budget
			spend_amount = budget - saved
			save = saved / budget
			spend = spend_amount / budget
		response_list.append({'name': event.name, 'saved': save, 'spent': spend})
	saving = 0
	allocated = 0
	for event in events:
		saved = get_ind_savings(event.id)
		if saved > 0:
			saving += saved
		allocated += event.allocated_budget
	response2_list = []
	response2_list.append({'name': 'Avg Saved per event', 'value': '$' + str(round(saving/len(events), 2))})
	response2_list.append({'name': 'Total Allocated', 'value': '$' + str(allocated)})
	response2_list.append({'name': 'Total Available to Spend', 'value': '$' + str(saving)})
	response_list.reverse()
	return json.dumps({"rows": response_list, "rows2": response2_list})