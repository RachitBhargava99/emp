from backend import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(160), unique = True, nullable = False)
	password = db.Column(db.String(64), nullable = False)
	isAdmin = db.Column(db.Boolean, nullable = False, default = False)
	name = db.Column(db.String(64), nullable = False)
	meal_pref = db.Column(db.Integer, nullable = False, default = 0)
##	rel = db.relationship('Relationship', backref = 'attendee', lazy = True)

	def get_auth_token(self, expires_seconds = 3600):
		s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.email}')"

class Event(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(255), nullable = False)
	description = db.Column(db.String(1023), nullable = False)
	mini_address = db.Column(db.String(255), nullable = False)
	address = db.Column(db.String(255), nullable = False)
	date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
	veg_price = db.Column(db.Float, nullable = False, default = 0.0)
	non_veg_price = db.Column(db.Float, nullable = False, default = 0.0)
	vegan_price = db.Column(db.Float, nullable = False, default = 0.0)
	allocated_budget = db.Column(db.Float, nullable = False, default = 0.0)
	eventbrite_id = db.Column(db.String(15), nullable = False)
##	rel = db.relationship('Relationship', backref = 'event', lazy = True)

	def __repr__(self):
		return f"Event('{self.name}')"

class Expense(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(255), nullable = False)
	value = db.Column(db.Float, nullable = False, default = 0.0)
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable = False)

class Relationship(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
	event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable = False)