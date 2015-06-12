import couchdb
import logging
import time

class RqDbAlreadyExistsError(Exception):
    pass
class RqDbCommunicationError(Exception):
    pass
class RqProjectDoesNotExistError(Exception):
    pass
class RqRequestDoesNotExistError(Exception):
    pass

class RqDb(object):
    def __init__(self, db_host):
        self.db_host = db_host
        self.couch_server = couchdb.Server(db_host)
        self.logger = logging.getLogger("RqDb")

    def get_project_by_key(self, key):
        view_result = self.couch_server['rqconfig'].view('doc/by_key', key=key)
        try:
            return list(view_result)[0].value
        except IndexError:
            raise RqProjectDoesNotExistError("Project with that key does not exist.")

    def get_project_by_name(self, name):
        view_result = self.couch_server['rqconfig'].view('doc/by_name', key=name)
        try:
            return list(view_result)[0].value
        except IndexError:
            raise RqProjectDoesNotExistError("Project with that name does not exist.")

    def get_all_projects(self):
        view_result = self.couch_server['rqconfig'].view('doc/by_type', key='project')
        return [project.value for project in list(view_result)]

    def send_message(self, message):
        try:
            self.couch_server['rqmessages'].save(message)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error sending message")

    def add_project_to_config(self, project):
        try:
            project.type = "project"
            self.couch_server["rqconfig"].save(project.__dict__)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while saving project to config database")

    def add_permission_to_project(self, project_name, perm_name):
        project = self.get_project_by_name(project_name)
        project['permissions'].append(perm_name)

        try:
            self.couch_server["rqconfig"][project['_id']] = project
        except couchdb.ResourceConflict:
            raise RqDbCommunicationError("Project resource conflict. Try again.")

    def create_permission_request(self, request):
        try:
            request.type = "request"
            self.couch_server["rqconfig"].save(request.__dict__)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while saving permission request to config database")

    def get_perm_request_by_id(self, request_id):
        try:
            request = self.couch_server["rqconfig"].get(request_id)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while getting permission request from config database")

        if request is None:
            raise RqRequestDoesNotExistError
        else:
            return request

    def update_perm_request(self, request_id, new_status):
        try:
            new_request = self.couch_server["rqconfig"].get(request_id)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while getting permission request from config database")
        if new_request is None:
            raise RqDbCommunicationError("Could not find request with that id")

        new_request['responded'] = int(time.time())
        new_request['status'] = new_status

        try:
            self.couch_server["rqconfig"][request_id] = new_request
        except couchdb.ResourceConflict:
            raise RqDbCommunicationError("Permission request resource conflict. Try again.")

        updated_request = self.couch_server["rqconfig"].get(request_id)
        if updated_request is None:
            raise RqDbCommunicationError("Could not find the updated request in the database")

        return updated_request