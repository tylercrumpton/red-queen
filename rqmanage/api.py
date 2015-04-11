from flask import Blueprint, make_response, jsonify, request, abort
from pymongo import MongoClient
from bson.objectid import ObjectId, InvalidId
import string
import random
import logging
import re

logger = logging.Logger(__name__)
RQ_VERSION = "v0.1.0"
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

manage_api = Blueprint("manage_api", __name__)
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client.rq
key_collection = db.keys
request_collection = db.requests
endpoint_collection = db.endpoints
message_collection = db.messages

class EndpointNotFoundError(Exception):
    def __init__(self):
        pass

class KeyNotFoundError(Exception):
    def __init__(self):
        pass

def generate_key(size=20, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_project_name(key_string):
    key = key_collection.find_one({'key': key_string})
    if key is None:
        return None
    else:
        return key["project_name"]

def is_valid_endpoint_name(name):
    # Make sure name only consists of letters, numbers, hyphens, and underscores:
    if not re.match(r"^[\w-]+$", name):
        return False
    else:
        return True

def add_permission_to_key(endpoint_name, key):
    if endpoint_collection.find_one({'endpoint_name': endpoint_name}) is None:
        raise EndpointNotFoundError
    if key_collection.find_one({'key': key}) is None:
        raise KeyNotFoundError
    key_collection.update({'key': key}, {"$addToSet": {'permissions': endpoint_name}})

@manage_api.route("/api/v1.0/version", methods=["GET"])
def get_api_version():
    return jsonify({'version': RQ_VERSION})

@manage_api.route('/api/v1.0/keys', methods=['POST'])
def create_key():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'owner_name' not in request.json:
        return make_response(jsonify({'error': 'No owner_name given'}), 400)
    if 'owner_email' not in request.json:
        return make_response(jsonify({'error': 'No owner_email given'}), 400)
    if 'project_name' not in request.json:
        return make_response(jsonify({'error': 'No project_name given'}), 400)
    if not is_valid_endpoint_name(request.json["project_name"]):
        return make_response(jsonify({'error': 'project_name is not valid; must consist of letters, digits, hyphens, '
                                               'and underscores'}), 400)
    # TODO: Email key info to owner

    keystring = generate_key(20)

    key = {
        'owner_name': request.json['owner_name'],
        'owner_email': request.json['owner_email'],
        'key': keystring,
        'permissions': [],
    }
    key_id = key_collection.insert_one(key).inserted_id

    key["_id"] = str(key_id)

    logger.info("New key created for {name}: {key}".format(name=key["owner_name"], key=keystring))
    return jsonify({'key': key}), 201

@manage_api.route('/api/v1.0/keys/<string:key_string>', methods=['GET'])
def get_key_permissions(key_string):

    key = key_collection.find_one({'key': key_string})
    if key is None:
        abort(404)

    # Stringify the _id:
    key["_id"] = str(key["_id"])

    return jsonify({'key': key}), 201

@manage_api.route('/api/v1.0/endpoints', methods=['POST'])
def create_endpoint():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'owner_name' not in request.json:
        return make_response(jsonify({'error': 'No owner_name given'}), 400)
    if 'owner_email' not in request.json:
        return make_response(jsonify({'error': 'No owner_email given'}), 400)
    if 'endpoint_name' not in request.json:
        return make_response(jsonify({'error': 'No endpoint_name given'}), 400)
    if not is_valid_endpoint_name(request.json['endpoint_name']):
        return make_response(jsonify({'error': 'endpoint_name is not valid; must consist of letters, digits, hyphens, '
                                               'and underscores'}), 400)
    if endpoint_collection.find_one({"endpoint_name": request.json['endpoint_name']}) is not None:
        return make_response(jsonify({'error': 'That endpoint_name already exists'}), 400)
    
    # TODO: Create RabbitMQ queue for endpoint

    endpoint = {
        'endpoint_name': request.json['endpoint_name'],
        'owner_name': request.json['owner_name'],
        'owner_email': request.json['owner_email'],
        'description': request.json.get('description', ''),
    }

    endpoint_id = endpoint_collection.insert_one(endpoint).inserted_id
    endpoint["_id"] = str(endpoint_id)

    logger.info("New endpoint created: {endpoint}".format(endpoint=endpoint["endpoint_name"]))
    return jsonify({'endpoint': endpoint}), 201

@manage_api.route('/api/v1.0/messages', methods=['POST'])
def send_message():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'target_endpoint' not in request.json:
        return make_response(jsonify({'error': 'No target_endpoint given'}), 400)
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)
    if 'data' not in request.json:
        return make_response(jsonify({'error': 'No data given'}), 400)

    key = key_collection.find_one({'key': request.json["key"]})
    if key is None:
        return make_response(jsonify({'error': 'Key not valid'}), 400)
    if request.json['target_endpoint'] not in key["permissions"]:
        return make_response(jsonify({'error': 'Key does not have permissions for that endpoint'}), 400)

    # TODO: Send message to correct queue

    message = {
        'target_endpoint': request.json['target_endpoint'],
        'sender_project_name': key["project_name"],
        'data': request.json['data'],
    }

    message_id = message_collection.insert_one(message).inserted_id
    message["_id"] = str(message_id)

    logger.info("New message posted to {endpoint}".format(endpoint=message["target_endpoint"]))

    return jsonify({'message': message}), 201

@manage_api.route('/api/v1.0/permissions/requests', methods=['POST'])
def request_permission():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'target_endpoint' not in request.json:
        return make_response(jsonify({'error': 'No target_endpoint given'}), 400)
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)

    requester_project_name = get_project_name(request.json['key'])
    if requester_project_name is None:
        return make_response(jsonify({'error': 'Key not valid'}), 400)

    # TODO: Send email to endpoint owner

    perm_request = {
        'target_endpoint': request.json['target_endpoint'],
        'requester_project_name': requester_project_name,
        'message': request.json.get('message', ''),
        'status': "pending",
    }

    request_id = request_collection.insert_one(perm_request).inserted_id
    perm_request["_id"] = str(request_id)

    logger.info("New request created for {endpoint}".format(endpoint=perm_request["target_endpoint"]))

    return jsonify({'request': perm_request}), 201

@manage_api.route('/api/v1.0/permissions/requests/<string:request_id>', methods=['PUT'])
def update_permission(request_id):
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'accept' not in request.json:
        return make_response(jsonify({'error': 'No accept given'}), 400)
    if type(request.json['accept']) is not bool:
        return make_response(jsonify({'error': 'accept is not a bool'}), 400)
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)

    # TODO: Send email to request sender

    perm_request = request_collection.find_one({'_id': ObjectId(request_id)})
    if perm_request is None:
        return make_response(jsonify({'error': 'Permission request not found'}), 404)

    key_project_name = get_project_name(request.json['key'])
    if key_project_name is None or not key_project_name == perm_request['target_endpoint']:
        return make_response(jsonify({'error': 'Key not valid'}), 400)

    if request.json['accept']:
        status = "accepted"
        add_permission_to_key(perm_request["target_endpoint"], request.json['key'])
    else:
        status = "denied"

    request_collection.update({'_id': ObjectId(request_id)}, {"$set": {'status': status}})

    return jsonify({'result': status}), 201

@manage_api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    from flask import Flask
    logging.basicConfig(level=logging.DEBUG)
    app = Flask(__name__)
    app.register_blueprint(manage_api)
    app.run(debug=True)
