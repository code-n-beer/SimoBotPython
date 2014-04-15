class Feature(object):

    handlers = {}
    command = ''
    handler = None

    def handle(self, msg, nick, channel):
        if self.handler:
            return self.handler(msg, nick, channel)
        return
