from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask import current_app


builtin_list = list

db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)

def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(160), unique = True, nullable = False)
    password = db.Column(db.String(64), nullable = False)
    isAdmin = db.Column(db.Boolean, nullable = False, default = False)
    events = db.relationship('Event', backref = 'attendee', lazy = True)

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
    mini_address = db.Column(db.String(255), nullable = False)
    address = db.Column(db.String(255), nullable = False)
    date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    attendee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bda4a008ed000ba841d4a11fb693ace86ed669db'
    app.config['PROJECT_ID'] = 'hackventure-emp'
    app.config['DATA_BACKEND'] = 'cloudsql'
    app.config['CLOUDSQL_USER'] = 'testuser'
    app.config['CLOUDSQL_PASSWORD'] = 'password'
    app.config['CLOUDSQL_DATABASE'] = 'emp_database'
    app.config['CLOUDSQL_CONNECTION_NAME'] = 'hackventure-emp:us-east1:emp-sql'
    app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+pymysql://{user}:{password}@localhost/{database}?unix_socket=/cloudsql/{connection_name}').format(user=app.config['CLOUDSQL_USER'], password=app.config['CLOUDSQL_PASSWORD'], database=app.config['CLOUDSQL_DATABASE'], connection_name=app.config['CLOUDSQL_CONNECTION_NAME'])
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")

if __name__ == '__main__':
    _create_database()