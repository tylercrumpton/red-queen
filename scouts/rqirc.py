import irc.bot
import irc.strings

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
            command = a[0].lstrip("!")
            arguments = None
            if len(a) > 1:
                arguments = a[1].strip()
            self.handle_command(event, command, arguments)
        return

    def handle_command(self, event, command, arguments):
        print command, ": ", arguments

if __name__ == "__main__":
    bot = RQBot("##rqtest", "PyRqBot", "chat.freenode.net", port=6667)
    bot.start()