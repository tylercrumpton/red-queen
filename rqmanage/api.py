from flask import Flask, make_response, jsonify, request, abort

RQ_VERSION = "v0.1.0"
app = Flask(__name__)

@app.route("/api/v1.0/version", methods=["GET"])
def get_api_version():
    return jsonify({'version': RQ_VERSION})

@app.route('/api/v1.0/endpoints', methods=['POST'])
def create_endpoint():
    if not request.json:
        return make_response(jsonify({'error': 'No request body given'}), 400)
    if 'endpoint_name' not in request.json:
        return make_response(jsonify({'error': 'No endpoint_name given'}), 400)
    if 'owner_name' not in request.json:
        return make_response(jsonify({'error': 'No owner_name given'}), 400)
    if 'owner_email' not in request.json:
        return make_response(jsonify({'error': 'No owner_email given'}), 400)
    endpoint = {
        'id': 1,
        'endpoint_name': request.json['endpoint_name'],
        'owner_name': request.json['owner_name'],
        'owner_email': request.json['owner_email'],
        'description': request.json.get('description', ''),
    }
    return jsonify({'endpoint': endpoint}), 201

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    app.run(debug=True)
