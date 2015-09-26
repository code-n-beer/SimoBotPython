import sys
sys.path.append('SyntaxMachine/src')
import main



class syntaxFeature:

    def __init__(self):
        main.load()

        self.cmdpairs = {
                    "!syntaxgen" : self.execute
                }

    def execute(self, queue, arg, msg, channel):
        arg = msg.split()

        #if len(arg) < 1:

        generatedSentence = main.generate()

        queue.put((generatedSentence, channel))
