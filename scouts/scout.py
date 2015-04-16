""" RedQueenScout is a class that a project can use to communication with Red Queen. It handles the communications
and protocols, leaving the developer to simply implement handlers for incoming data or use it to send messages of its
own.
"""


class RedQueenScout(object):
    def __init__(self, rq_ip, rq_port):
        self.queen_ip = rq_ip
        self.queen_port = rq_port
    def send_message(self, endpoint, data):
        pass
    def add_listener(self, endpoint, callback):
        pass