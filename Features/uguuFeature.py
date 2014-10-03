
import random

class reverseFeature:

    def __init__(self):
       self.cmdpairs = {
            "!uguu" : self.execute
            }


    def execute(self, queue, nick, msg, channel):
        nick = msg.split()
        if len(nick) < 2:
            print "nothing to uguu"
            return

        nick = nick[1]

        count = random.randint(1,16);
        uguu = nick + ("u" * count)
        print "executed varjouguu"
        queue.put((uguu, channel))
