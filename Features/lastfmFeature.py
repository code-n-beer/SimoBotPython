import pylast, ConfigParser, os, json, redis

class lastfmFeature:

        config = ConfigParser.ConfigParser()
        config.read("Resources/settings.cfg")
        network = pylast.LastFMNetwork(
                api_key=config.get('lastfm','API_KEY'),
                api_secret=config.get('lastfm','API_SECRET'))
        redishost = config.get("redis", "redishost")
        redisport = config.get("redis", "redisport")
        redisdb = config.get("lastfm", "redisdb")
        r = redis.StrictRedis(redishost, int(redisport), redisdb)

        def __init__(self):
            self.cmdpairs = {
                    "!np" : self.execute,
                    "!setlastfm" : self.setlastfm
                            }

        def setlastfm(self, queue, nick, message, channel):
            try:
                lastfmname = message.split()[1]
            except IndexError:
                queue.put(("Give a last.fm username", channel))
                return
            self.r.set(nick, lastfmname)
            output = "%s's last.fm username now set to %s" %(nick, lastfmname)
            print output
            queue.put((output, channel))

        def execute(self, queue, nick, message, channel):
            msg = message.split()

            if len(msg) < 2:
                lastfmname = self.r.get(nick)
                if lastfmname:
                    user = self.network.get_user(lastfmname)
                else:
                    print "No username set for %s" %nick
                    queue.put(("No last.fm username set, try !setlastfm <username>", channel))
                    return
            else:
                user = self.network.get_user(msg[1])

            try:
                trackData = user.get_now_playing()
                if trackData:
                    output = "%s is playing: " %user
                else:
                    trackData = user.get_recent_tracks(limit=1)[0][0]
                    output = "%s played: " %user
            except:
                err = "Couldn't retrieve now playing or last played track"
                print err
                queue.put((err, channel))
                return

            artist = trackData.get_artist().get_name()
            track = trackData.get_title()
            rawtags = pylast.extract_items(trackData.get_top_tags(limit=3))
            tags = ', '.join([x.get_name() for x in rawtags])
            if tags:
                tags = "<" + tags + ">"
            output += artist + " - " + track + " " + tags
            queue.put((output, channel))
