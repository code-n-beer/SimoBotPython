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
                "!tweet" : self.tweet,
                "!follow" : self.follow,
                "!unfollow" :self.unfollow
                }
        self.twitter = Twitter(auth=self.auth)

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
        if len(tweet) > 280:
            print "tweet limit 280 characters"
            queue.put(("Tweet limit is 280 characters", channel))
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
