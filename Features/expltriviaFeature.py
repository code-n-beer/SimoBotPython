import random
import redis
import ConfigParser


class explTriviaFeature:

  config = ConfigParser.ConfigParser()
  config.read("Resources/settings.cfg")
  redisport = config.get("expl", "redisport")
  redisdb = config.get("expl", "redisdb")

  def __init__(self):
      self.cmdpairs = {
        "!trivia"   : self.newQuestion,
        "!answer"   : self.answer,
        "!hiscore"  : self.hiscores
      }
      self.connect(self.redisport, self.redisdb)

  def connect(self, p, d):
    self.redis = redis.StrictRedis(host='localhost', port=p, db=d)
    self.redisAnswer = redis.StrictRedis(host='localhost', port=p, db=15)
    self.redisHS = redis.StrictRedis(host='localhost', port=p, db=14)

  def newQuestion(self, queue, nick, msg, channel):
    ses = str(self.redisAnswer.get("answer"))
    print ses
    if self.redisAnswer.exists("answer"):
        queue.put(("What expl? (" + str(self.redisAnswer.get("points")) + " points)  " + str(self.redisAnswer.get("question")), channel))
        return
    answer = self.redis.randomkey()
    r = random.randint(0,self.redis.llen(answer)-1)
    question = self.redis.lindex(answer, r)
    self.redisAnswer.set("question", question)
    self.redisAnswer.set("answer", answer)
    self.redisAnswer.set("points", 1)
    queue.put(("What expl? (1 point)  "+str(question), channel))


  def answer(self, queue, nick, msg, channel):
    answer = str(self.redisAnswer.get("answer"))
    simomsg = ""
    msg = msg.split(' ', 1)
    qpoints = str(self.redisAnswer.get("points"))
    if self.redisHS.exists(nick):
        points = int(self.redisHS.get(nick))
    else:
        points = 0
    if msg[1].encode('utf-8').lower().find(answer) != -1:
        apoints = int(qpoints)
        self.redisHS.set(nick, points+apoints)
        simomsg = simomsg +"Correct! "+nick+" has been awarded "+str(apoints)+" points."
        self.redisAnswer.delete("answer")
        self.redisAnswer.delete("question")
    else:
        simomsg = simomsg +"Wrong. This question is now worth " + str(int(qpoints)+1) + " points."
        self.redisAnswer.set("points",int(qpoints)+1)
    queue.put((simomsg, channel))

  def hiscores(self, queue, nick, msg, channel):
      msg = msg.split(' ')
      if len(msg) < 2:
        #kaikki hiscoret
        queue.put(("Not implemented", channel))
      else:
          name = msg[1].strip()
          if self.redisHS.exists(name):
              ret = name + " : " + str(self.redisHS.get(name)) + " points"
          else:
              ret = "No hiscores found for " + name
          queue.put((ret, channel))
