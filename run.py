# Run a test server:
from app import app
import logging

logging.basicConfig()
app.run(host='0.0.0.0', port=8080, debug=True)
