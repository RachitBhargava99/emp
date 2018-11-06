import backend
from backend.models import User, Event, Expense, Relationship
import json

def get_ind_savings(event_id):
	relationships = Relationship.query.filter_by(event_id = event_id)
	response_list = []
	for relationship in relationships:
		user_p = User.query.filter_by(id = relationship.user_id).first()
		response_list.append({'id': user_p.id, 'name': user_p.name, 'email': user_p.email, 'meal_pref': user_p.meal_pref})
	users = response_list
	veg, nonveg, vegan = meal_div_users(users)
	
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
	return remaining_amount

def meal_div_users(users):
	veg = 0
	non_veg = 0
	vegan = 0
	for user in users:
		if user['meal_pref'] == 0:
			veg += 1
		elif user['meal_pref'] == 1:
			non_veg += 1
		elif user['meal_pref'] == 2:
			vegan += 1
	return (veg, non_veg, vegan)