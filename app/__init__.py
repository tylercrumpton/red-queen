from flask import Flask
from app.management.routes import manage_api
from pymongo import MongoClient
from management.db import RqDb

# Define the WSGI application object:
app = Flask(__name__)

# Load config file:
app.config.from_object('config')

# Connect to the DB:
# TODO: Add this to config file
MONGO_HOST = '10.0.0.1'
MONGO_PORT = 27017
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client.rq
COUCH_HOST = 'https://user:pass@redqueenurl.net/couch'

rq_db = RqDb(COUCH_HOST)
# Register blueprint(s)
app.register_blueprint(manage_api)