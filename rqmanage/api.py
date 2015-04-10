from flask import Blueprint, make_response, jsonify, request, abort
from pymongo import MongoClient
from bson.objectid import ObjectId, InvalidId
import string
import random
import logging

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


def generate_key(size=20, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_owner(key_string):
    key = key_collection.find_one({'key': key_string})
    if key is None:
        return None
    else:
        return key["_id"]

def is_valid_endpoint_name(name):
    # Make sure name only consists of letters, numbers, hyphens, and underscores:
    if not re.match(r"^[\w-]+$", name):
        return False
    else:
        return True

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
    if 'endpoint_name' not in request.json:
        return make_response(jsonify({'error': 'No endpoint_name given'}), 400)
    if not is_valid_endpoint_name(request.json['endpoint_name']):
        return make_response(jsonify({'error': 'endpoint_name is not valid; must consist of letters, digits, hyphens, '
                                               'and underscores'}), 400)
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)

    owner_id = get_owner(request.json['key'])
    if owner_id is None:
        return make_response(jsonify({'error': 'Key not valid'}), 400)

    # TODO: Create RabbitMQ queue for endpoint

    endpoint = {
        'endpoint_name': request.json['endpoint_name'],
        'owner_id': owner_id,
        'description': request.json.get('description', ''),
    }

    endpoint_id = endpoint_collection.insert_one(endpoint).inserted_id
    endpoint["_id"] = str(endpoint_id)
    endpoint["owner_id"] = str(owner_id)

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

    sender_id = get_owner(request.json['key'])
    if sender_id is None:
        return make_response(jsonify({'error': 'Key not valid'}), 400)

    # TODO: Validate key against endpoint
    # TODO: Send message to correct queue

    message = {
        '_id': 1,
        'target_endpoint': request.json['target_endpoint'],
        'sender_id': sender_id,
        'data': request.json['data'],
    }

    message_id = message_collection.insert_one(message).inserted_id
    message["_id"] = str(message_id)
    message["sender_id"] = str(sender_id)

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

    requester_id = get_owner(request.json['key'])
    if requester_id is None:
        return make_response(jsonify({'error': 'Key not valid'}), 400)

    # TODO: Send email to endpoint owner

    perm_request = {
        'target_endpoint': request.json['target_endpoint'],
        'requester_id': requester_id,
        'message': request.json.get('message', ''),
    }

    request_id = request_collection.insert_one(perm_request).inserted_id
    perm_request["_id"] = str(request_id)
    perm_request["requester_id"] = str(requester_id)

    logger.info("New request created for {endpoint}".format(endpoint=perm_request["target_endpoint"]))

    return jsonify({'request': perm_request}), 201

@manage_api.route('/api/v1.0/permissions/requests/<int:request_id>', methods=['PUT'])
def update_permission(request_id):
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'accept' not in request.json:
        return make_response(jsonify({'error': 'No accept given'}), 400)
    if type(request.json['accept']) is not bool:
        return make_response(jsonify({'error': 'accept is not a bool'}), 400)
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)

    endpoint_owner_id = get_owner(request.json['key'])
    if endpoint_owner_id is None:
        return make_response(jsonify({'error': 'Key not valid'}), 400)

    # TODO: Update request in DB
    # TODO: Send email to request sender
    # TODO: Retrieve actual request from DB
    # TODO: Add endpoint to key's list of permissions in DB

    perm_request = {
        '_id': request_id,
        'target_endpoint': "target",
        'endpoint_owner_id': endpoint_owner_id,
        'requester': "bob",
        'message': "my request",
        "accepted": request.json['accept'],
    }
    perm_request["endpoint_owner_id"] = str(endpoint_owner_id)
    return jsonify({'request': perm_request}), 201

@manage_api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    from flask import Flask
    logging.basicConfig(level=logging.DEBUG)
    app = Flask(__name__)
    app.register_blueprint(manage_api)
    app.run(debug=True)
