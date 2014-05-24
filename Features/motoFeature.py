# coding=utf8
import random

def vittu():
    if random.randint(0, 8) < 4:
        return "mee ny vittuu "
    else:
        return ""

def mouth():
    s = "_"

    for i in range(0, random.randint(0, 32)):
        s = s + "_"

    return s

def face():
    return vittu() + "/" + mouth() + "\\"

class motoFeature:
    def __init__(self):
        self.cmdpairs = { "!mötö" : self.execute }

    def execute(self, queue, nick, msg, channel):
        try:
            target = msg.split()[1] + ": "
        except IndexError:
            target = ""

        text = target + face()
        print text
        queue.put((text, channel))
