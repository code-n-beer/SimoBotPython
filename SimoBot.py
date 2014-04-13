from irc.client import SimpleIRCClient
import logging

logging.basicConfig(level=logging.DEBUG)


class SimoBot(SimpleIRCClient):

    def __init__(self, server, port, nick, channels=[]):
        super(SimoBot, self).__init__()
        self.connection.set_rate_limit(1)
        self.server = server
        self.port = port
        self.nick = nick
        self.channels = channels

    def send_to_chan(self, chan, msg):
        self.connection.privmsg(chan, msg)

    def on_nicknameinuse(self, c, e):
        self.nick = c.nickname + "_"
        c.nick(self.nick)

    def on_welcome(self, c, e):
        for channel in self.channels:
            c.join(channel)

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        logging.debug("message on " + e.target +
                      ": <" + e.source.nick + "> " + msg)

    def start(self):
        self.connect(server=self.server,
                     port=self.port,
                     nickname=self.nick)
        super(SimoBot, self).start()