class Feature(object):

    handlers = {}
    command = ''
    handler = None

    def handle(self, msg, nick):
        if self.handler:
            return self.handler(msg, nick)
        return
