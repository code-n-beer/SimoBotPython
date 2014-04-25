import random
import redis

class explFeature:
  
  
  def __init__(self):
    self.cmdpairs = {
        "!varjoexpl"   : self.explain,
        "!varjoadd"    : self.add,
        "!varjoremove" : self.remove
    }
    self.msglength = 380 
    self.connect(6379, 7)

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
    ret = topic + "[" + str(explIndex) + "/{}] : "
    index = 0
    length = len(ret)
    page = 1
    while index < len(explrange):
      addString = str(index + 1) + ") " + explrange[index] + "  "
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
    queue.put((ret.format(page), channel))  


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
    self.redis.rpush(msg[1], msg[2])
    queue.put(("New expl added!", channel))

  def remove(self, queue, nick, msg, channel):
    queue.put(("Not implemented yet", channel))

