# coding=utf8
import random

def vittu():
    if random.randint(0, 8) < 4:
        return "mee ny vittuu "
    else:
        return ""

def tuu():
    if random.randint(0, 8) < 4:
        return "tuus ny tänne "
    else:
        return ""

def mouth():
    s = "_"

    for i in range(0, random.randint(0, 32)):
        s = s + "_"

    return s

def face():
    return vittu() + "/" + mouth() + "\\"

def happyface():
    return tuu() + "^" + mouth() + "^"

class motoFeature:
    def __init__(self):
        self.cmdpairs = {
                u"!mötö" : self.execute,
                u"!unmötö" : self.execute2
                }

    def execute(self, queue, nick, msg, channel):
        try:
            target = msg.split()[1] + ": "
        except IndexError:
            target = ""

        text = target + face()
        queue.put((text, channel))

    def execute2(self, queue, nick, msg, channel):
        try:
            target = msg.split()[1] + ": "
        except IndexError:
            target = ""

        text = target + happyface()
        queue.put((text, channel))

