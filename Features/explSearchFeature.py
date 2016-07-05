import redis
from explFeature import getMsg
import ConfigParser

class explSearchFeature:
  config = ConfigParser.ConfigParser()
  config.read("Resources/settings.cfg")
  msglength = 380
  redisport = config.get("expl", "redisport")
  redisdb = config.get("expl", "redisdb")

  def __init__(self):
    self.cmdpairs = {
        "!find"   : self.find
    }
    self.connect(int(self.redisport), self.redisdb)

  def connect(self, p, d):
    self.redis = redis.StrictRedis(host='localhost', port=p, db=d)

  def find(self, queue, nick, msg, channel):
    msg = msg.split()
    topic = msg[1].lower()
    content = msg[2]
    queue.put((getMsg(topic, None, content), channel))
