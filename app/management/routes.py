from flask import Blueprint, request, make_response
from app.management.models import RqMessages, RqProjects, RqRequests
from bson import json_util
from bson.objectid import ObjectId
import time
from db import RqDbAlreadyExistsError, RqDbCommunicationError, RqProjectDoesNotExistError
import app
import logging

logger = logging.getLogger(__name__)
manage_api = Blueprint('manage', __name__, url_prefix='/api/v1.0')

def json_response(response):
    new_response = make_response(response)
    new_response.headers['Content-type'] = 'application/json'
    return new_response

@manage_api.route("/version", methods=["GET"])
def get_rq_version():
    # TODO: Make this actually grab a version number
    return json_response(json_util.dumps({'version': "v0.1.0"}))

@manage_api.route('/projects', methods=['POST'])
def create_project():
    try:
        project = RqProjects(request.json)
    except KeyError as e:
        return json_response(json_util.dumps({'error': "No '%s' given" % e}))
    try:
        app.rq_db.add_project_to_config(project)
    except RqDbAlreadyExistsError as e:
        return json_response((json_util.dumps({'error': str(e)})))
    except Exception as e:
        logger.exception(e)
        return json_response((json_util.dumps({'error': "Unknown error occurred while trying to create database"})))
    return json_response(json_util.dumps(project.__dict__))

@manage_api.route('/projects', methods=['GET'])
def list_projects():
    project_list = list(app.db.projects.find())

    # Yank out emails and keys:
    for project in project_list:
        del project['key']
        del project['owner']['email']

    return json_response(json_util.dumps(project_list))

@manage_api.route('/projects/<string:name>', methods=['GET'])
def get_project(name):
    project = app.db.projects.find_one({'name': name})

    if project is None:
        return json_response(json_util.dumps({'error': "Project with name '%s' does not exist" % name}))

    # Yank out email and key:
    del project['key']
    del project['owner']['email']

    return json_response(json_util.dumps(project))

@manage_api.route('/messages', methods=['POST'])
def send_message():
    try:
        message = RqMessages(request.json)
    except KeyError as e:
        return json_response(json_util.dumps({'error': 'No %s given' % e}))
    except RqProjectDoesNotExistError:
        return json_response(json_util.dumps({'error': 'No project exists for that key'}))
    except TypeError:
        return json_response(json_util.dumps({'error': 'Incorrect content-type'}))

    try:
        dest_project = app.rq_db.get_project_by_name(message.destination)
    except RqProjectDoesNotExistError:
        return json_response(json_util.dumps({'error': "Destination '%s' does not exist." % message.destination}))
    sender_project = app.rq_db.get_project_by_name(message.sender)

    if dest_project['name'] not in sender_project['permissions']:
        if message.destination != message.sender:
            return json_response(json_util.dumps({'error': "Project '{}' does not have permissions for destination '{}'.".format(message.sender, message.destination)}))

    # Send the message off to the destinations API:
    try:
        message = message.__dict__
        app.rq_db.send_message(message)
        return json_response(json_util.dumps(message))
    except:
        return json_response(json_util.dumps({'error': "Error sending message to CouchDB."}))

@manage_api.route('/messages/<string:message_id>', methods=['GET'])
def get_message(message_id):
    message = app.db.messages.find_one({'_id': ObjectId(message_id)})

    if message is None:
        return json_response(json_util.dumps({'error': "Message with id '%s' does not exist" % message_id}))

    return json_response(json_util.dumps(message))

@manage_api.route('/requests', methods=['POST'])
def create_request():
    try:
        perm_request = RqRequests(request.json)
    except KeyError as e:
        return json_response(json_util.dumps({'error': "No '%s' given" % e}))
    except RqProjectDoesNotExistError:
        return json_response(json_util.dumps({'error': 'No project exists for that key'}))

    try:
        dest_project = app.rq_db.get_project_by_name(perm_request.destination)
    except RqProjectDoesNotExistError:
        return json_response(json_util.dumps({'error': "Destination '%s' does not exist." % perm_request.destination}))
    sender_project = app.rq_db.get_project_by_name(perm_request.sender)

    if dest_project['name'] in sender_project['permissions']:
        return json_response(json_util.dumps({'error': "Project '{}' already permissions for destination '{}'.".format(perm_request.sender, perm_request.destination)}))
    elif perm_request.destination == perm_request.sender:
        return json_response(json_util.dumps({'error': "Project cannot request permissions from itself"}))
    app.rq_db.create_permission_request(perm_request)

    # TODO: Email requested destination project owner

    return json_response(json_util.dumps(perm_request.__dict__))

@manage_api.route('/requests/<string:request_id>', methods=['GET'])
def get_request(request_id):
    perm_request = app.db.requests.find_one({'_id': ObjectId(request_id)})

    if perm_request is None:
        return json_response(json_util.dumps({'error': "Request with id '%s' does not exist" % request_id}))

    return json_response(json_util.dumps(perm_request))

@manage_api.route('/requests/<string:request_id>', methods=['PUT'])
def resolve_request(request_id):
    try:
        perm_request = app.rq_db.get_perm_request_by_id(request_id)
    except RqDbCommunicationError as e:
        return json_response((json_util.dumps({'error': str(e)})))

    if perm_request['status'] == 'accepted':
        return json_response(json_util.dumps({'error': "Request with id '%s' has already been accepted" % request_id}))
    elif perm_request['status'] == 'rejected':
        return json_response(json_util.dumps({'error': "Request with id '%s' has already been rejected" % request_id}))

    try:
        project = app.rq_db.get_project_by_key(request.json['key'])
        accept = request.json['accept']
    except KeyError as e:
        return json_response(json_util.dumps({'error': "No '%s' given" % e}))
    except RqProjectDoesNotExistError:
        return json_response(json_util.dumps({'error': 'No project exists for that key'}))
    except Exception as e:
        return json_response((json_util.dumps({'error': "Unknown error occurred while trying to retrieve project from key"})))

    if not project['name'] == perm_request['destination']:
        return json_response(json_util.dumps({'error': "Project '{}' cannot accept request for project '{}".format(project["name"], perm_request['destination'])}))

    if accept:
        perm_request["status"] = 'accepted'
        # Add project to list of permissions:
        #app.db.projects.update_one({'name': perm_request['sender']},
        #                           {'$addToSet': {'permissions': perm_request['destination']}})
    else:
        perm_request["status"] = 'rejected'

    updated_request = app.rq_db.update_perm_request(perm_request.id, perm_request)

    # TODO: Email request sender

    return json_response(json_util.dumps(updated_request))

