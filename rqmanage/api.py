from flask import Flask, make_response, jsonify, request

RQ_VERSION = "v0.1.0"
app = Flask(__name__)


def get_owner(key):
    return "tylercrumpton"

@app.route("/api/v1.0/version", methods=["GET"])
def get_api_version():
    return jsonify({'version': RQ_VERSION})

@app.route('/api/v1.0/keys', methods=['POST'])
def create_key():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'owner_name' not in request.json:
        return make_response(jsonify({'error': 'No owner_name given'}), 400)
    if 'owner_email' not in request.json:
        return make_response(jsonify({'error': 'No owner_email given'}), 400)

    # TODO: Generate real id number
    # TODO: Add key to DB
    # TODO: Generate real key

    key = {
        'id': 1,
        'owner_name': request.json['owner_name'],
        'owner_email': request.json['owner_email'],
        'key': '1234',
    }

    return jsonify({'key': key}), 201

@app.route('/api/v1.0/endpoints', methods=['POST'])
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
        'id': 1,
        'endpoint_name': request.json['endpoint_name'],
        'owner_name': get_owner(request.json['key']),
        'description': request.json.get('description', ''),
    }

    return jsonify({'endpoint': endpoint}), 201

@app.route('/api/v1.0/messages', methods=['POST'])
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
        'id': 1,
        'target_endpoint': request.json['target_endpoint'],
        'sender': get_owner(request.json['key']),
        'data': request.json['data'],
    }

    return jsonify({'message': message}), 201

@app.route('/api/v1.0/permissions/requests', methods=['POST'])
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
        'id': 1,
        'target_endpoint': request.json['target_endpoint'],
        'requester': get_owner(request.json['key']),
        'message': request.json.get('data', ''),
    }

    return jsonify({'request': perm_request}), 201

@app.route('/api/v1.0/permissions/requests/<int:request_id>', methods=['PUT'])
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
        'id': request_id,
        'target_endpoint': "target",
        'endpoint_owner': get_owner(request.json['key']),
        'requester': "bob",
        'message': "my request",
        "accepted": request.json['accept'],
    }

    return jsonify({'request': perm_request}), 201

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    app.run(debug=True)
