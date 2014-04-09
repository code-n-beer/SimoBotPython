
class uguuFeature:

    #cmd = "!varjor"
    def __init__(self):
       self.cmdpairs = {
            "!varjor" : self.execute
            }

    def execute(self, queue, nick, message, channel):
        msg = " ".join(message.split()[1:])
        msg = msg[::-1]
        print "testink: " + msg
        queue.put((nick, msg, channel))
