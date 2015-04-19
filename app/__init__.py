from flask import Flask
from app.management.routes import manage_api
from pymongo import MongoClient

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

# Register blueprint(s)
app.register_blueprint(manage_api)