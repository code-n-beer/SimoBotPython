import ConfigParser, redis, signal

class gallupFeature:

    config = ConfigParser.ConfigParser()
    config.read("Resources/settings.cfg")
    redisport = config.get("gallup", "redisport")
    redisdb = config.get("gallup", "redisdb")

    onGoing = False
    startedBy = "" #nick of user who started the gallup
    endTime = None
    title = ""
    options = []
    answered = [] # list of users who have already answered the gallup (yes, you can circumvent it by changing your nick)

    def __init__(self):
        self.cmdpairs = {
                "!gallup" : self.gallup,
                "!endgallup" : self.endCheck,
                "!answergallup" : self.answer
        }
        self.connect(int(self.redisport, self.redisdb))

    def connect(self, p, d):
        self.redis = redis.strictRedis(host='localhost', port=p, db=d)
        self.statsRedis = redis.strictReis(host='localhost', port=p, db=17)


    def gallup(self, client, channel, user, line)
        if onGoing:
                client.put((channel, title + " | Ends in " + str(round(signal.getitimer(signal.ITIMER_REAL), 0)) + " min"))
                return
        onGoing = True
        startedBy = user.replace("_", "")
        self.client = client
        self.channel = channel
        line = line.split('#')
        title = line[0]
            options = map(lambda x:[x,0], line[1:])
        client.put((channel, "Started gallup: " + title + " Options: " + self.printOptions(False)))
        signal.signal(signal.SIGALRM, self.handler)
        endTime = signal.setitimer(signal.ITIMER_REAL, 12 * 60 * 60)


    def answer(self, client, channel, user, line):
        if not onGoing:
                client.put((channel, "No ongoing gallup. Start a new one by saying !gallup #Ass or boobs? #Ass #Boobs #Neither, I like ice cream"))
                return

        if answered.indexOf(user.replace("_", "")) != -1
                client.put((channel, "You have already answered this gallup"))
                return
        answered.append(user)

        line = line.split(' ', 1)[1]

        accepted = False
        if int(line) < options.length: #given answer is an index of options
            options[int(line)][1] += 1
            accepted = True
        else: #compare answer to options as string
            for opt in options:
                if line.replace(' ', '') == opt[0]:
                    opt[1] += 1
                    accepted = True
                    break
        if accepted:
            client.put((channel, "Answer recorded."))
        else:
            client.put((channel, "Invalid answer. Question was " + question + " Options are " + self.printOptions(False)))


    def endCheck(self, client, channel, user, line)
        if not onGoing:
                client.put((channel, "No ongoing gallup. Start a new one by saying !gallup #Ass or boobs? #Ass #Boobs #Neither, I like ice cream"))
                return
        if user != startedBy:
                client.put((channel, "You can't end this gallup because you didn't start it. Gallup ends in " + str(round(signal.getitimer(signal.ITIMER_REAL)/ 60, 0)) + " min"))
                return
        self.end(client, channel)


    def end(self):
        signal.alarm(0)
        answered = []
        options = []
        title = ""
        #save results

        self.client.put((self.channel, "Gallup " + title + " ended. Results: " + self.printOptions(True)))
        onGoing = False


    def printOptions(self, answers):
        if not onGoing:
            return
        ret = ""
        i = 0
        is answers:
            numberOfAnswers = reduce(lambda x, y: x[1]+y[1], options
        for opt in options:
            ret += "(" + i + ") " + str(opt[0]) + " "
            if answers:
                ret += opt[1] + " answers (" + str(round(opt[1] / numberOfAnswers, 1)) + " % "
        return ret


    def handler(self, signum, frame):
        self.end()
