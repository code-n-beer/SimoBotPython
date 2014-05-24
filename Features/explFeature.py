import random
import redis
import ConfigParser

class explFeature:

  config = ConfigParser.ConfigParser()
  config.read("Resources/settings.cfg")
  msglength = 380
  redisport = config.get("expl", "redisport")
  redisdb = config.get("expl", "redisdb")

  def __init__(self):
    self.cmdpairs = {
        "!expl"   : self.explain,
        "!add"    : self.add,
        "!remove" : self.remove
    }
    self.connect(self.redisport, self.redisdb)

  def connect(self, p, d):
    self.redis = redis.StrictRedis(host='localhost', port=p, db=d)


  def explain(self, queue, nick, msg, channel):
    msg = msg.split()
    explIndex = 1
    if len(msg) < 2:
      topic = self.redis.randomkey()
      if topic == None:
        queue.put(("Expl database empty!", channel))
        return
    else:
      topic = msg[1].lower() 
      if len(msg) > 2:
        explIndex = msg[2]
        if not explIndex.isdigit():
          queue.put(("Invalid expl index!", channel))
          return
        else:
          explIndex = int(explIndex)
    queue.put((self.getMsg(topic, explIndex), channel))

  def getMsg(self, topic, explIndex):
    if (not self.redis.exists(topic)):
      return "No such expl"
    explrange = self.redis.lrange(topic, 0, self.redis.llen(topic))
    header = (topic + "{} : ").encode('utf-8')
    index = 0
    page = 1
    length = 0
    ret = ""
    while index < len(explrange):
      addString = "\x02[\x0309" + str(index + 1) + "\x0F\x02]\x0F " + explrange[index].rstrip()  + "\x0F "
      nextLength = len(addString)
      #CASE: too long expl
      if nextLength + len(header) > self.msglength:
        index += 1
        continue
      #CASE: page full
      if length + nextLength + len(header) > self.msglength:
        page += 1
        length = 0
        if explIndex == 0:
          ret = ""
      length += nextLength
      if page == explIndex or explIndex == 0:
        ret += addString
      index += 1
    if explIndex > page:
      return "Invalid expl index"
    if explIndex == 0:
      explIndex = page
    if page == 1:
      return header.format("") + ret
    else:
      return header.format("[" + str(explIndex) + "/" + str(page) + "]") + ret


  def add(self, queue, nick, msg, channel):
    msg = msg.split(' ', 2)
    if len(msg) != 3:
      queue.put(("Usage: !add <topic> <expl>", channel))
      return
    if len(msg[1]) > 64:
      queue.put(("Maximum expl topic length is 64 chars", channel))
      return
    if len(msg[2]) > self.msglength:
      queue.put(("Expl too long, not added", channel))
      return
    self.redis.rpush(msg[1].lower(), msg[2].rstrip())
    queue.put((self.getMsg(msg[1], 0), channel))

  def remove(self, queue, nick, msg, channel):
    msg = msg.lower().split()
    if len(msg) == 2:
      if not self.redis.exists(msg[1]):
        queue.put(("No such expl", channel))
        return
      self.redis.delete(msg[1])
      queue.put(("Removed one expl topic!", channel))
      return
    elif len(msg) != 3:
      queue.put(("usage: !remove <topic> [index]", channel))
      return
    elif not self.redis.exists(msg[1]):
      queue.put(("no such expl", channel))
      return
    elif int(msg[2]) <= 0 or int(msg[2]) > self.redis.llen(msg[1]):
      queue.put(("bad index", channel))
      return
    if int(msg[2]) == 1:
      newRangeHead = {}
    else:
      newRangeHead = self.redis.lrange(msg[1], 0, int(msg[2]) - 2)
    print(newRangeHead)
    newRangeTail = self.redis.lrange(msg[1], int(msg[2]), self.redis.llen(msg[1]))
    self.redis.delete(msg[1])
    for i in newRangeHead:
      self.redis.rpush(msg[1], i)
    for i in newRangeTail:
      self.redis.rpush(msg[1], i)
    queue.put(("Deleted one expl item!", channel))

