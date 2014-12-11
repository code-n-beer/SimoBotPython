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
			"!trivia"   : self.question,
			"!answer"   : self.answer,
			"!hiscore"  : self.hiscores
		}
		self.connect(int(self.redisport), self.redisdb)

	def connect(self, p, d):
		self.redis = redis.StrictRedis(host='localhost', port=p, db=d)
		self.redisAnswer = redis.StrictRedis(host='localhost', port=p, db=15)
		self.redisHS = redis.StrictRedis(host='localhost', port=p, db=14)

	def question(self, queue, nick, msg, channel):
		ses = str(self.redisAnswer.get("answer"))
		if self.redisAnswer.exists("answer"):
			qpoints = self.redisAnswer.get("points")
			simomsg = "What expl? (" + str(qpoints) + " points)  " + str(self.redisAnswer.get("question"))
			if int(qpoints) < 5:
				simomsg = simomsg + " | " + str(self.redisAnswer.get("hint1"))
			if int(qpoints) < 3:
				simomsg = simomsg + " | " + str(self.redisAnswer.get("hint2"))
			queue.put((simomsg, channel))
			return
		question = ""
		explSize = 0
		while (len(question)<3 or explSize<3):
			answer = self.redis.randomkey()
			explSize = self.redis.llen(answer)
			r = random.randint(0, explSize - 1)
			question = self.redis.lindex(answer, r)
		r2 = r
		while (r2 == r):
			r2 = random.randint(0, explSize - 1)
		r3 = r
		while (r3 == r2 or r3 == r):
			r3 = random.randint(0, explSize - 1)
		self.redisAnswer.set("question", question)
		self.redisAnswer.set("hint1", self.redis.lindex(answer, r2))
		self.redisAnswer.set("hint2", self.redis.lindex(answer, r3))
		self.redisAnswer.set("answer", answer)
		self.redisAnswer.set("points", 5)
		queue.put(("What expl? (5 points)  "+str(question), channel))


	def answer(self, queue, nick, msg, channel):
		if self.redisAnswer.exists("answer") != 1:
			return
		answer = str(self.redisAnswer.get("answer"))
		simomsg = ""
		msg = msg.split(' ', 1)
		qpoints = str(self.redisAnswer.get("points"))

		if msg[1].encode('utf-8').lower().find(answer) != -1:
			if self.redisHS.exists(nick):
				points = int(self.redisHS.get(nick))
			else:
				points = 0
			apoints = int(qpoints)
			self.redisHS.set(nick, points+apoints)
			simomsg = "Correct! "+nick+" has been awarded "+str(apoints)+" points."
			self.redisAnswer.delete("answer")
			self.redisAnswer.delete("question")
		else:
			if int(qpoints) < 2:
				simomsg = "Wrong. The correct answer was " + str(self.redisAnswer.get("answer"))+"."
				self.redisAnswer.delete("answer")
				self.redisAnswer.delete("question")
			else:
				simomsg = "Wrong. What expl? " + str(self.redisAnswer.get("question")) + " | " + str(self.redisAnswer.get("hint1"))
				if int(qpoints) <5:
					simomsg = simomsg + " | " + str(self.redisAnswer.get("hint2"))
				simomsg = simomsg + " (" + str(int(qpoints)-2) + " points)"
				self.redisAnswer.set("points",int(qpoints)-2)
		queue.put((simomsg, channel))

	def hiscores(self, queue, nick, msg, channel):
		msg = msg.split(' ')
		if len(msg) < 2:
        #kaikki hiscoret
			queue.put(("Not implemented", channel))
			return
		name = msg[1].strip()
		if self.redisHS.exists(name):
			ret = name + " : " + str(self.redisHS.get(name)) + " points"
		else:
			ret = "No hiscores found for " + name
		queue.put((ret, channel))
