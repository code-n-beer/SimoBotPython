from twitter import *
import ConfigParser, os
import re

class twitterFeature:

    config = ConfigParser.ConfigParser()
    config.read("Resources/settings.cfg")
    auth = OAuth(
        config.get('twitter','OAUTH_TOKEN'),
        config.get('twitter','OAUTH_SECRET'),
        config.get('twitter','CONSUMER_KEY'),
        config.get('twitter','CONSUMER_SECRET'))

    def __init__(self):
        self.cmdpairs = {
                "!twitter" : self.execute,
                "!tweet" : self.tweet,
                "!follow" : self.follow,
                "!unfollow" :self.unfollow
                }
        self.twitter = Twitter(auth=self.auth)

    #Read tweets from userstream
    def execute(self, queue, nick, msg, channel):
        stream = TwitterStream(auth=self.auth, domain='userstream.twitter.com')
        print "Opened Twitter userstream"
        queue.put(("Opened Twitter userstream", channel))
        try:
            for msg in stream.user():
                try:
                    if msg['user']['id'] != 1220480214: # Dont read own tweets
                        user = msg['user']['name']
                        text = msg['text']
                        queue.put(("Tweet from %s: %s" %(user, text), channel))
                except KeyError:
                    # Not a tweet (favourite/retweet etc.)
                    pass
                #Disconnect messages
                try:
                    #reason = msg['disconnect']['reason']
                    reason = self.disconnectCode(msg['disconnect']['code'])
                    queue.put(("Twitter stream disconnected: %s" %(reason), channel))
                except KeyError:
                    pass
        except TwitterError, e:
            print "Twitter stream disconnected: %s" %e
            shorte = str(e).split("details: ",1)[1]
            queue.put(("Twitter stream disconnected: %s" %shorte, channel))

    def disconnectCode(self, code):
        codes = {
                1: u"Shutdown",
                2: u"Duplicate stream",
                3: u"Control request",
                4: u"Stall",
                5: u"Normal",
                6: u"Token revoked",
                7: u"Admin logout",
                9: u"Max message limit",
                10: u"Stream exception",
                11: u"Broker stall",
                12: u"Shed load",
                }
        return codes[int(code)]

    def follow(self, queue, nick, msg, channel):
        name = msg.split()[1].strip()
        if re.search(r'[^\w]', name) or not (1 <= len(name) <= 15):
            print "invalid username"
            queue.put(("Invalid username", channel))
            return

        try:
            user = self.twitter.friendships.lookup(screen_name=name, _method='GET')
        except TwitterError:
            print "Username %s not found" %(name)
            queue.put(("Username not found", channel))
            return

        if "following" in user[0]['connections']:
            print "Already following %s" %(user[0]['name'])
            queue.put(("Already following %s" %(user[0]['name']), channel))
            return

        try:
            self.twitter.friendships.create(screen_name=name)
        except TwitterError:
            print "Twitter error, following failed"
            queue.put(("Following failed", channel))
        print "executed follow"
        queue.put(("Now following %s" %(user[0]['name']), channel))

    def unfollow(self, queue, nick, msg, channel):
        name = msg.split()[1].strip()
        if re.search(r'[^\w]', name) or not (1 <= len(name) <= 15):
            print "invalid username"
            queue.put(("invalid username", channel))
            return

        try:
            user = self.twitter.friendships.lookup(screen_name=name, _method='GET')
        except TwitterError:
            print "Twitter error"
            queue.put(("Couldn't unfollow %s" %(name), channel))
            return

        try:
            if "following" in user[0]['connections']:
                self.twitter.friendships.destroy(screen_name=name)
                print "No longer following %s" %(user[0]['name'])
                queue.put(("No longer following %s" %(user[0]['name']), channel))
                print "executed unfollow"
                return
        except IndexError:
            print "Username not found"
            queue.put(("Username not found", channel))
            return
        except TwitterError:
            print "TwitterError"
            queue.put(("Couldn't unfollow %" %(name), channel))
            return

        print "executed unfollow"
        queue.put(("Wasn't following %s" %(user[0]['name']), channel))

    def tweet(self, queue, nick, msg, channel):
        tweet = msg[7:]
        if len(tweet) > 140:
            print "tweet limit 140 characters"
            queue.put(("Tweet limit is 140 characters", channel))
            return
        elif len(msg.split()) < 2:
            print "nothing to tweet"
            queue.put(("Nothing to tweet", channel))
            return

        try:
            self.twitter.statuses.update(status=tweet)
        except TwitterError:
            print "%sTweeting failed" %(get_prefix('error'))
            queue.put(("Tweeting failed", channel))
            return

        print "executed tweet"
        queue.put(("Tweeted succesfully", channel))
