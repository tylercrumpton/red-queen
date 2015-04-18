import string
import random
from datetime import datetime

def generate_key():
    size = 20
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def get_project_by_key(key):
    # TODO implement this search
    return "projectname"


class RqProjects(object):
    def __init__(self, request_dict):
        self.name = request_dict['name']
        self.created = datetime.utcnow()
        self.owner = dict(name=request_dict['owner']['name'],
                          email=request_dict['owner']['email'],
                          nick=request_dict['owner']['nick'])
        self.key = generate_key()
        self.permissions = list()
        self.description = request_dict['description']

class RqMessages(object):
    def __init__(self, request_dict):
        self.type = request_dict['type']
        self.created = datetime.utcnow()
        self.sender = get_project_by_key(request_dict['key'])
        self.data = request_dict['data']
        self.destination = request_dict['destination']

class RqRequests(object):
    def __init__(self, request_dict):
        self.status = "pending"
        self.created = datetime.utcnow()
        self.responded = None
        self.sender = get_project_by_key(request_dict['key'])
        self.target = request_dict['target']
        self.description = request_dict['description']