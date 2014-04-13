from twitter import *
import ConfigParser, os

class twitterFeature:

    config = ConfigParser.ConfigParser()
    config.read("Resources/settings.cfg")
    oToken = config.get('twitter','OAUTH_TOKEN')
    oSecret = config.get('twitter','OAUTH_SECRET')
    cKey = config.get('twitter','CONSUMER_KEY')
    cSecret = config.get('twitter','CONSUMER_SECRET')

    def __init__(self):
        self.cmdpairs = {
    #            "!twitter" : self.execute,
                "!tweet" : self.tweet#,
    #            "!follow" : self.follow,
    #            "!unfollow" :self.unfollow
                }
        self.twitter = Twitter(
            auth=OAuth(
                self.oToken, self.oSecret, self.cKey, self.cSecret))

    #Read tweets from users followed
    #def execute(self, queue, nick, msg, channel):
    #    print "no function yet"

    #Follow user
    #def follow(self, queue, nick, msg, channel):
    #    name = msg.split()[1]
    #    # Doesnt work with Twitter API 1.1, statuses.friends 404s
    #    following = [x['name'] for x in self.twitter.statuses.friends()]
    #    if (name in friends):
    #        print "Already following %s" %(name)
    #        queue.put(("Already following %s" %(name), channel))
    #    else:
    #        try:
    #            self.twitter.friendships.create(screen_name=name)
    #        except TwitterError:
    #            print "Unable to follow %s" % (name)
    #            queue.put(("%sUnable to follow %s, are you sure the name is correct?" %(
    #                get_prefix('error'), name)))
    #            return

    #    print "executed follow"
    #    queue.put(("Now following %s!" %(name)))

    #Unfollow user
    #def unfollow(self, queue, nick, msg, channel):
    #    print "no function yet"

    def tweet(self, queue, nick, msg, channel):
        tweet = msg[7:]
        if len(tweet) > 140:
            print "tweet limit 140 characters"
            queue.put(("tweet limit is 140 characters", channel))
            return
        elif len(msg.split()) < 2:
            print "nothing to tweet"
            queue.put(("nothing to tweet", channel))
            return

        try:
            self.twitter.statuses.update(status=tweet)
        except TwitterError:
            print "%sTweeting failed" %(get_prefix('error'))
            queue.put(("Tweeting failed", channel))
            return

        print "executed tweet"
        queue.put(("tweeted succesfully", channel))
