print "one"
print "one"
print "one"
import sys
import os.path
print "two"
print "two"
print "two"
sys.path.append(os.path.join(os.path.dirname(__file__), 'SyntaxMachine/src'))
print "three"
print "three"
print "three"
from handler import Handler
print "four"
print "four"
print "four"


class syntaxFeature:

    def __init__(self):
	print "initializing syntax feature"
	print "initializing syntax feature"
	print "initializing syntax feature"
	print "initializing syntax feature"
	self.h = Handler()
        self.h.load()
	print "loaded syntax feature"

        self.cmdpairs = {
                    "!syntaxgen" : self.execute
                }

    def execute(self, queue, arg, msg, channel):
	print "ses";
        arg = msg.split()
	print "ses";

        #if len(arg) < 1:
	print "ses";

        generatedSentence = self.h.generate()
	print generatedSentence

        queue.put((generatedSentence, channel))
