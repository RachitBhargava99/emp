class Config:
	SECRET_KEY = 'bda4a008ed000ba841d4a11fb693ace86ed669db'
##	SQLALCHEMY_DATABASE_URI = 'sqlite://' + os.getcwd().replace('\\', '/') + 'site.db'
	PROJECT_ID = 'hackventure-emp'
	DATA_BACKEND = 'cloudsql'
	CLOUDSQL_USER = 'testuser'
	CLOUDSQL_PASSWORD = 'password'
	CLOUDSQL_DATABASE = 'emp_database'
	CLOUDSQL_CONNECTION_NAME = 'hackventure-emp:us-east1:emp-sql'
	SQLALCHEMY_DATABASE_URI = ('mysql+pymysql://{user}:{password}@localhost/{database}?unix_socket=/cloudsql/{connection_name}').format(user=CLOUDSQL_USER, password=CLOUDSQL_PASSWORD, database=CLOUDSQL_DATABASE, connection_name=CLOUDSQL_CONNECTION_NAME)
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAPS_API = 'AIzaSyAs5sA8X7MR-vbuNNxfJ4a-xSiUeOLtg-U'
	EVENTBRITE_API = 'IDRVAZ64JV6QIV3GHNDX'
	ORGANIZATION_ID = 266092106870
	ORGANIZER_ID = 18054883646