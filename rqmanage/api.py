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

def get_owner(key):
    return "tylercrumpton"

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
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)

    # TODO: Generate real id number
    # TODO: Add endpoint to DB
    # TODO: Create RabbitMQ queue for endpoint

    endpoint = {
        '_id': 1,
        'endpoint_name': request.json['endpoint_name'],
        'owner_name': get_owner(request.json['key']),
        'description': request.json.get('description', ''),
    }

    logger.info("New endpoint created by {name}: {endpoint}".format(name=endpoint["owner_name"],
                                                                    endpoint=endpoint["endpoint_name"]))
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

    # TODO: Generate real id number
    # TODO: Add message to DB
    # TODO: Validate key against endpoint
    # TODO: Send message to correct queue

    message = {
        '_id': 1,
        'target_endpoint': request.json['target_endpoint'],
        'sender': get_owner(request.json['key']),
        'data': request.json['data'],
    }

    logger.info("New message posted by {name} to {endpoint}".format(name=message["sender"],
                                                                    endpoint=message["target_endpoint"]))

    return jsonify({'message': message}), 201

@manage_api.route('/api/v1.0/permissions/requests', methods=['POST'])
def request_permission():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'target_endpoint' not in request.json:
        return make_response(jsonify({'error': 'No target_endpoint given'}), 400)
    if 'key' not in request.json:
        return make_response(jsonify({'error': 'No key given'}), 400)

    # TODO: Generate real id number
    # TODO: Add request to DB
    # TODO: Send email to endpoint owner

    perm_request = {
        '_id': 1,
        'target_endpoint': request.json['target_endpoint'],
        'requester': get_owner(request.json['key']),
        'message': request.json.get('data', ''),
    }

    logger.info("New request created by {name} for {endpoint}".format(name=perm_request["requester"],
                                                                      endpoint=perm_request["target_endpoint"]))

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

    # TODO: Update request in DB
    # TODO: Send email to request sender
    # TODO: Retrieve actual request from DB
    # TODO: Add endpoint to key's list of permissions in DB

    perm_request = {
        '_id': request_id,
        'target_endpoint': "target",
        'endpoint_owner': get_owner(request.json['key']),
        'requester': "bob",
        'message': "my request",
        "accepted": request.json['accept'],
    }

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
