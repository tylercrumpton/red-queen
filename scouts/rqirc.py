import irc.bot
import irc.strings
from flask import Flask, request, jsonify
import requests
import threading

class RQBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nick, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nick, nick)
        self.channel = channel

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        if event.arguments[0][0] == "!":
            a = event.arguments[0].split(" ", 1)
            command = a[0].lstrip("!").rstrip(' ')
            arguments = None
            if len(a) > 1:
                arguments = a[1].strip()
            self.handle_command(event, command, arguments)
        return

    def handle_command(self, event, command, arguments):
        print "{command}: {arguments}".format(command=command, arguments=arguments)


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
    return "OK"

if __name__ == "__main__":
    bot = RQBot("#btctiptest", "PyRqBot", "chat.freenode.net", port=6667)
    irc_thread = threading.Thread(target=bot.start)
    api_thread = threading.Thread(target=run_api)
    irc_thread.start()
    api_thread.start()