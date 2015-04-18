from flask import Flask
from ming import create_datastore, Session
# Define the WSGI application object:
app = Flask(__name__)

# Load config file:
app.config.from_object('config')

# Connect to the DB:
# TODO: Add this to config file
bind = create_datastore('mongodb://10.0.0.1:27017', database="rq")
session = Session(bind)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.management.routes import manage_api

# Register blueprint(s)
app.register_blueprint(manage_api)