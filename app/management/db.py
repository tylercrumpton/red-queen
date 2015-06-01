import requests
import couchdb
import logging
from models import RqRequests, RqProjects, RqMessages

class RqDbAlreadyExistsError(Exception):
    pass
class RqDbCommunicationError(Exception):
    pass

class RqDb(object):
    def __init__(self, db_host):
        self.db_host = db_host
        self.couch_server = couchdb.Server(db_host)
        self.logger = logging.getLogger("RqDb")

    def send_message(self, message, destination):
        try:
            self.couch_server[destination].save(message)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error sending message")

    def create_project_db(self, project_name):
        # Create the project database:
        try:
            self.couch_server.create(project_name)
        except couchdb.PreconditionFailed:
            raise RqDbAlreadyExistsError("Project with name '%s' already exists" % project_name)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while creating database")

        # Save the permissions document:
        permissions_doc = {
            "admins": {"names": [], "roles": ["admins"]},
            "members": {"names": [], "roles": []}
        }
        try:
            self.couch_server[project_name].security = permissions_doc
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while saving permissions to database")

        # Make the database read-only for un-authenticated users:
        readonly_script = {"validate_doc_update":"function(newDoc, oldDoc, userCtx) {   if (userCtx.roles.indexOf('_admin') !== -1) {     return;   } else {     throw({forbidden: 'This DB is read-only'});   }   } "}
        try:
            self.couch_server[project_name]["_design/auth"] = readonly_script
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while saving read-only script to database")

    def add_project_to_config(self, project):
        try:
            project.type = "project"
            self.couch_server["rqconfig"].save(project.__dict__)
        except Exception as e:
            self.logger.exception(e)
            raise RqDbCommunicationError("Unknown error while saving project to config database")