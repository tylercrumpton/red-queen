from rq.api import manage_api
from flask import Flask
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.register_blueprint(manage_api)
app.run(debug=True)