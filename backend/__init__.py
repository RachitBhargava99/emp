import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from backend.config import Config
##import mysql.connector

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
mail = Mail()
##cnx = mysql.connector.connect(user = app.config.CLOUDSQL_USER, password = app.config.CLOUDSQL_PASSWORD, database = app.config.CLOUDSQL_DATABASE, connection = app.config.CLOUDSQL_CONNECTION_NAME)
##cursor = cnx.cursor()

def create_app():
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)

	from backend.users.routes import users
	from backend.events.routes import events
	from backend.finance.routes import finance
	app.register_blueprint(users)
	app.register_blueprint(events)
	app.register_blueprint(finance)

	return app