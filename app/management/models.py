import string
import random
import time
import app

def generate_key():
    size = 20
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


class RqProjects(object):
    def __init__(self, request_dict):
        self.name = request_dict['name']
        self.created = int(time.time())
        self.owner = dict(name=request_dict['owner']['name'],
                          email=request_dict['owner']['email'],
                          nick=request_dict['owner']['nick'])
        self.key = generate_key()
        self.permissions = list()
        self.description = request_dict['description']

class RqMessages(object):
    def __init__(self, request_dict):
        self.type = request_dict['type']
        self.created = int(time.time())
        self.sender = app.rq_db.get_project_by_key(request_dict['key'])["name"]
        self.data = request_dict['data']
        self.destination = request_dict['destination']

class RqRequests(object):
    def __init__(self, request_dict):
        self.status = "pending"
        self.created = int(time.time())
        self.responded = None
        self.sender = app.rq_db.get_project_by_key(request_dict['key'])["name"]
        self.destination = request_dict['destination']
        self.description = request_dict['description']