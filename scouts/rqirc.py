import irc.bot
import irc.strings
from flask import Flask, request, jsonify
import requests
from gevent import monkey
from gevent.pywsgi import WSGIServer
import gevent
monkey.patch_all()

class RQBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nick, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nick, nick)
        self.channel = channel

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        command = event.arguments[0]
        if command.lower().startswith("!rq"):
            self.send_command(event, command)
        return

    def send_command(self, event, command):
        irc_message = {'type': event.type,
                       'source': event.source,
                       'target': event.target,
                       'arguments': event.arguments}
        print "'{command}' command detected in channel {chan}".format(command=command, chan=event.target)


def send_message(destination, data, msg_type="event"):
    payload = {'type': msg_type,
               'key': '261brqmt1p68jshm0key',
               'destination': destination,
               'data': data}
    r = requests.post("http://0.0.0.0:8080/api/v1.0/messages", data=jsonify(payload), timeout=1)

app = Flask(__name__)

def run_api():
    app.run(host='0.0.0.0', port=9090, debug=False)

@app.route('/message', methods=['POST'])
def receive_message():
    print request.json
    bot.connection.privmsg("BLAH")
    return "OK"

if __name__ == "__main__":
    print "Logging into IRC..."
    bot = RQBot("#btctiptest", "PyRqBot", "chat.freenode.net", port=6667)
    gevent.spawn(bot.start)
    print "Spinning up the API..."
    api = WSGIServer(('', 9090), app)
    api.serve_forever()