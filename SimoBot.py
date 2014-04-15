import inspect
import multiprocessing
import os
import pkgutil
from irc.client import SimpleIRCClient
import logging
from Features.feature import Feature
from helpers.commandparser import CommandParser


class SimoBot(SimpleIRCClient):

    features = CommandParser()
    channels = []

    def __init__(self, server, port, nick, channels=None):
        super(SimoBot, self).__init__()
        self.connection.set_rate_limit(2)
        self.server = server
        self.port = port
        self.nick = nick
        if channels:
            self.channels = channels

    def send_to_chan(self, chan, msg):
        self.connection.privmsg(chan, msg)

    def load_all_features(self):
        logging.info('Loading features')
        features = __import__('Features')
        features_iter = pkgutil.iter_modules(features.__path__)
        for (loader, name, ispkg) in features_iter:
            try:
                module = loader.find_module(name).load_module(name)
                self.load_feature_from_module(module)
            except SyntaxError as e:
                logging.error("Syntax error in " + os.path.basename(e.filename))
            except ImportError as e:
                errors = ", ".join(e.args)
                logging.error("Import error in " + name + ": " + errors)

    def load_feature_from_module(self, module):
        for (name, class_) in inspect.getmembers(module, inspect.isclass):
            if issubclass(class_, Feature) and class_ is not Feature:
                module = 'Features.' + class_.__module__
                (connection, simo_connection) = multiprocessing.Pipe()
                p = multiprocessing.Process(
                    target=run_feature,
                    args=(module, name, connection))
                p.daemon = True
                p.start()
                command = simo_connection.recv()
                self.features.add(command, (simo_connection, p))
                logging.info('Loaded ' + name)

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
        parsed = self.features.parse(msg)
        if parsed and parsed.handler[1].is_alive():
            pipe = parsed.handler[0]
            pipe.send((parsed.arguments, e.source.nick))
            if pipe.poll(5):
                response = pipe.recv()
                self.send_to_chan(e.target, response)

    def start(self):
        self.connect(server=self.server,
                     port=self.port,
                     nickname=self.nick)
        self.load_all_features()
        super(SimoBot, self).start()


def run_feature(module, classname, connection):
    feature_module = __import__(module, fromlist=[classname])
    feature = getattr(feature_module, classname)()

    connection.send(feature.command)

    while True:
        try:
            msg, nick = connection.recv()
            connection.send(feature.handle(msg, nick))
        except (EOFError, IOError):
            logging.warning('Subprocess for ' + classname + ' terminating!')
            break
