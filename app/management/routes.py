from flask import Blueprint, request, make_response
from app.management.models import RqMessages, RqProjects, RqRequests, ApiKeyNotFoundError
from bson import json_util
import app

manage_api = Blueprint('manage', __name__, url_prefix='/api/v1.0')

@manage_api.route("/version", methods=["GET"])
def get_rq_version():
    # TODO: Make this actually grab a version number
    return json_util.dumps({'version': "v0.1.0"})

@manage_api.route('/projects', methods=['POST'])
def create_project():
    try:
        project = RqProjects(request.json)
    except KeyError as e:
        return make_response(json_util.dumps({'error': "No '%s' given" % e}))
    app.db.projects.insert(project.__dict__)
    return json_util.dumps(project.__dict__)

@manage_api.route('/projects', methods=['GET'])
def list_projects():
    pass

@manage_api.route('/projects/<string:name>', methods=['GET'])
def get_project(name):
    pass

@manage_api.route('/messages', methods=['POST'])
def send_message():
    try:
        message = RqMessages(request.json)
    except KeyError as e:
        return make_response(json_util.dumps({'error': 'No %s given' % e}))
    except ApiKeyNotFoundError:
        return make_response(json_util.dumps({'error': 'No project exists for that key'}))

    dest_project = app.db.projects.find_one({'name': message.destination})
    sender_project = app.db.projects.find_one({'name': message.sender})
    if dest_project is None:
        return make_response(json_util.dumps({'error': "Destination '%s' does not exist." % message.destination}))
    elif dest_project['name'] not in sender_project['permissions']:
        if message.destination != message.sender:
            return make_response(json_util.dumps({'error': "Project '{}' does not have permissions for destination '{}'.".format(message.sender, message.destination)}))
    app.db.messages.insert(message.__dict__)
    return json_util.dumps(message.__dict__)

@manage_api.route('/messages/<string:id>', methods=['GET'])
def get_message():
    pass

@manage_api.route('/requests', methods=['POST'])
def create_request():
    try:
        perm_request = RqRequests(request.json)
    except KeyError as e:
        return make_response(json_util.dumps({'error': 'No %s given' % e}))
    return json_util.dumps(perm_request.__dict__)

@manage_api.route('/permissions/requests/<string:id>', methods=['GET'])
def get_request(id):
    pass

@manage_api.route('/permissions/requests/<string:id>', methods=['PUT'])
def resolve_request(id):
    pass



