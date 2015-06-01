import requests
import couchdb
import logging
from bson import json_util

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
        headers = {'Content-Type': 'application/json'}
        return requests.post("{host}/{db}".format(host=self.db_host, db=destination),
                             data=message, timeout=1, headers=headers)

    def create_project_db(self, project_name):
        # Create the project database:
        try:
            self.couch_server.create(project_name)
        except couchdb.PreconditionFailed:
            raise RqDbAlreadyExistsError("Project with name '%s' already exists" % project_name)
        except Exception as e:
            self.logger.error(e)
            raise RqDbCommunicationError("Unknown error while creating database")

        # Save the permissions document:
        permissions_doc = {
            "admins": {"names": [], "roles": ["admins"]},
            "members": {"names": [], "roles": []}
        }
        try:
            self.couch_server[project_name].security = permissions_doc
        except Exception as e:
            self.logger.error(e)
            raise RqDbCommunicationError("Unknown error while saving permissions to database")

        # Make the database read-only for un-authenticated users:
        readonly_script = {"validate_doc_update":"function(newDoc, oldDoc, userCtx) {   if (userCtx.roles.indexOf('_admin') !== -1) {     return;   } else {     throw({forbidden: 'This DB is read-only'});   }   } "}
        try:
            self.couch_server[project_name]["_design/auth"] = readonly_script
        except Exception as e:
            self.logger.error(e)
            raise RqDbCommunicationError("Unknown error while saving read-only scropt to database")
