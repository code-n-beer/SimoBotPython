import os
import pkgutil
from irc.client import SimpleIRCClient
import logging

class SimoBot(SimpleIRCClient):

    def __init__(self, server, port, nick, channels=None):
        super(SimoBot, self).__init__()
        self.connection.set_rate_limit(1)
        self.server = server
        self.port = port
        self.nick = nick
        if not channels:
            channels = []
        self.channels = channels

    def send_to_chan(self, chan, msg):
        self.connection.privmsg(chan, msg)

    def load_all_features(self):
        features = __import__('Features')

        features_iter = pkgutil.iter_modules(features.__path__)
        for (loader, name, ispkg) in features_iter:
            try:
                loader.find_module(name).load_module(name)
            except SyntaxError as e:
                logging.error("Syntax error in " + os.path.basename(e.filename))
            except ImportError as e:
                errors = ", ".join(e.args)
                logging.error("Import error in " + name + ": " + errors)

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
        self.load_all_features()
        super(SimoBot, self).start()