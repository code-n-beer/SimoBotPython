import random
import redis
import ConfigParser

class hangmanFeature:

  config = ConfigParser.ConfigParser()
  config.read("Resources/settings.cfg")
  msglength = 380
  redisport = config.get("expl", "redisport")
  redisdb = config.get("expl", "redisdb")

  def __init__(self):
    self.cmdpairs = {
        "!hirsi"   : self.hang,
    }
    self.connect(int(self.redisport), self.redisdb)

  def connect(self, p, d):
    self.redis = redis.StrictRedis(host='localhost', port=p, db=d)
    self.hirsiRedis = redis.StrictRedis(host='localhost', port=p, db=15)

  def hang(self, queue, nick, msg, channel):
    msg = msg.split()
    gameInProgress = self.hirsiRedis.exists("hirsiAnswer")
    ret = ""
    if gameInProgress and msg.length > 1:
      ret += self.guess(msg[1])
    if not gameInProgress:
      self.newGame()
    ret += self.displaySituation()
    queue.put((ret, channel))

  def guess(self, letter):
    letter = letter.lower()
    alreadyGuessed = self.hirsiRedis.get("hirsiGuessed").find(letter)
    if alreadyGuessed:
      return letter + " has already been guessed."
    self.hirsiRedis.append("hirsiGuessed", letter)
    containsLetter = self.hirsiRedis.get("hirsiAnswer").find(letter)
    if containsLetter:
      return "Yay! Showing all " + letter
    self.hirsiRedis.decr("hirsiGuessesLeft")
    return "No luck for " + letter

  def displaySituation(self):
    soFar = self.hirsiRedis.get("hirsiAnswerSoFar")
    guessesLeft = self.hirsiRedis.get("hirsiGuessesLeft")
    if soFar.find("*") == -1:
      return sofar + "| You win!"
    if guessesLeft == 0:
      return self.hirsiRedis.get("hirsiAnswer") + "| You are dead."
    return soFar + "| Wrong guesses until death: " + guessesLeft
	  
  def newGame(self):
    answer = ""
    while (len(answer) < 5 or self.isNotAlpha(answer)):
      expl = self.redis.randomkey()
      explSize = self.redis.llen(answer)
      i = random.randint(0, explSize - 1)
      answer = self.redis.lindex(expl, i)
    answer = answer.lower()
    self.hirsiRedis.set("hirsiAnswer", answer)	
    self.hirsiRedis.set("hirsiAnswerSoFar", "*" * len(answer))
    self.hirsiRedis.set("hirsiGuessesLeft", 8)
    self.hirsiRedis.set("hirsiGuessed", "")
	  
  def showLetters(self, letter):
    word = self.hirsiRedis.get("hirsiAnswer")
    wordSoFar = self.hirsiRedis.get("hirsiAnswerSoFar")
    for x in range (0, len(word)):
      if word[x] == letter:
	wordSoFar[x] = letter
    self.hirsiRedis.set("hirsiAnswerSoFar", wordSoFar) 

  def isNotAlpha(self, expl):
    spacesRemoved = expl.replace(" ", "a")
    return not spacesRemoved.isalpha()
