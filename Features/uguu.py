import random
from Features.feature import Feature


class UguuFeature (Feature):

    def __init__(self):
        self.command = '!uguu'
        self.handler = UguuFeature.execute

    @staticmethod
    def execute(msg, nick, channel):
        if len(msg) > 0:
            nick = msg
        else:
            nick = random.sample(channel, 1)[0]
        count = random.randint(1,16)
        return nick + ('u' * count) + '~'
