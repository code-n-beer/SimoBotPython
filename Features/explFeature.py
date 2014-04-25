import random
import redis

class explFeature:
  
  config = ConfigParser.ConfigParser() 
  config.read("Resources/settings.cfg")
  self.msglength = config.get("expl", "msglength")
  self.redisport = config.get("expl", "redisport")
  self.redisdb = config.get("expl", "redisdb")

  def __init__(self):
    self.cmdpairs = {
        "!varjoexpl"   : self.explain,
        "!varjoadd"    : self.add,
        "!varjoremove" : self.remove
    }
    self.connect(redisport, redisdb)

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
      if(not self.redis.exists(topic)):
        queue.put(("No such expl", channel))
        return
      if len(msg) > 2:
        explIndex = int(msg[2])
        if explIndex <= 0:
          queue.put(("Invalid expl index", channel))
          return
    explrange = self.redis.lrange(topic, 0, self.redis.llen(topic))
    ret = (topic + "{} : ").encode('utf-8')
    index = 0
    length = len(ret)
    page = 1
    while index < len(explrange):
      addString = "|" + str(index + 1) + "| " + explrange[index].rstrip()  + "  "
      nextLength = len(addString)
      #ignore too long expls (in case any get through anyway)
      if nextLength > self.msglength:
        index += 1
        continue
      if length + nextLength > self.msglength:
        page += 1
        length = 0
      length += nextLength
      if page == explIndex:
        ret += addString
      index += 1
    if explIndex > page:
      queue.put(("Invalid expl index", channel))
      return
    if page == 1:
      ret = ret.format("")
    else:
      ret = ret.format("[" + str(explIndex) + "/" + str(page) + "]")
    queue.put((ret, channel))  



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
    self.redis.rpush(msg[1], msg[2].rstrip())
    queue.put(("New expl added!", channel))

  def remove(self, queue, nick, msg, channel):
    msg = msg.split()
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

