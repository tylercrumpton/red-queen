from ming import Field, Session
from ming.declarative import Document
from ming import schema as S

import string
import random
from datetime import datetime

session = Session()  # ming abstraction for database

def generate_key():
    size = 20
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

Owner = dict(name=str, email=str, nick=str)

class RqProjects(Document):
    class __mongometa__:
        session = session
        name = 'rq.projects'
        indexes = ['name']
    _id = Field(S.ObjectId)
    name = Field(str)
    created = Field(datetime, if_missing=datetime.utcnow)
    owner = Field(Owner)
    key = Field(str, if_missing=generate_key)
    permissions = Field([str], if_missing=[])
    description = Field(str)

class RqMessages(Document):
    class __mongometa__:
        session = session
        name = 'rq.messages'
    _id = Field(S.ObjectId)
    type = Field(str)
    created = Field(datetime, if_missing=datetime.utcnow)
    sender = Field(str)
    data = Field(dict)
    destination = Field(str)

class RqRequests(Document):
    class __mongometa__:
        session = session
        name = 'rq.requests'
    _id = Field(S.ObjectId)
    status = Field(str)
    created = Field(datetime, if_missing=datetime.utcnow)
    responded = Field(datetime, if_missing=datetime.utcnow)
    sender = Field(str)
    target = Field(str)
    description = Field(str)