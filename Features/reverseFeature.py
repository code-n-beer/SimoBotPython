
class uguuFeature:

    #cmd = "!varjor"
    def __init__(self):
       self.cmdpairs = {
            "!r" : self.execute
            }

    def execute(self, queue, nick, message, channel):
        msg = " ".join(message.split()[1:])
        msg = msg[::-1]
        queue.put((msg, channel))
