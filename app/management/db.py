import requests
from bson import json_util

class RqDbAlreadyExistsError(Exception):
    pass
class RqDbCommunicationError(Exception):
    pass

class RqDb(object):
    def __init__(self, db_host):
        self.db_host = db_host

    def send_message(self, message, destination):
        headers = {'Content-Type': 'application/json'}
        return requests.post("{host}/{db}".format(host=self.db_host, db=destination),
                             data=message, timeout=1, headers=headers)

    def create_project_db(self, project_name):
        r = requests.put("{host}/{db}".format(host=self.db_host, db=project_name),
                         timeout=5)
        if r.status_code == 412:
            raise RqDbAlreadyExistsError("Project with name '%s' already exists" % project_name)
        elif r.status_code != 201:
            raise RqDbCommunicationError("Error creating database")

        permissions_dict = {
            "admins": {"names": [], "roles": ["admins"]},
            "members": {"names": [], "roles": []}
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.put("{host}/{db}/_security".format(host=self.db_host, db=project_name),
                         data=json_util.dumps(permissions_dict), timeout=5, headers=headers)
        if r.status_code != 201 and r.status_code != 200:
            raise RqDbCommunicationError("Error setting security permissions")

        readonly_script = {"validate_doc_update":"function(newDoc, oldDoc, userCtx) {   if (userCtx.roles.indexOf('_admin') !== -1) {     return;   } else {     throw({forbidden: 'This DB is read-only'});   }   } "}
        r = requests.put("{host}/{db}/_design/auth".format(host=self.db_host, db=project_name),
                         data=json_util.dumps(readonly_script), timeout=5, headers=headers)
        if r.status_code != 201 and r.status_code != 200:
            raise RqDbCommunicationError("Error updating readonly script")
