from irc.client import SimpleIRCClient
import logging

logging.basicConfig(level=logging.DEBUG)

class SimoBot(SimpleIRCClient):

    def __init__(self, server, port, nick):
        super(SimoBot, self).__init__()
        self.connect(server=server,
                     port=port,
                     nickname=nick)

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        logging.debug("message on " + e.target +
                      ": <" + e.source.nick + "> " + msg)