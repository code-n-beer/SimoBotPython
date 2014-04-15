import random
from Features.feature import Feature


class UguuFeature (Feature):

    def __init__(self):
        self.command = '!uguu'
        self.handler = UguuFeature.execute

    @staticmethod
    def execute(msg, nick):
        if len(msg) > 0:
            nick = msg
        count = random.randint(1,16)
        return nick + ("u" * count)
