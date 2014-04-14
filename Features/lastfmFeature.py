import pylast, ConfigParser, os, json

class lastfmFeature:

        config = ConfigParser.ConfigParser()
        config.read("Resources/settings.cfg")
        network = pylast.LastFMNetwork(
                api_key=config.get('lastfm','API_KEY'),
                api_secret=config.get('lastfm','API_SECRET'))

        def __init__(self):
            self.cmdpairs = {
                    "!varjonp" : self.execute,
        #            "!varjosetlastfm" : self.setlastfm
                            }

        #def setlastfm(self, queue, nick, message, channel):
        #    print "Not yet implemented"

        def execute(self, queue, nick, message, channel):
            msg = message.split()

            if len(msg) < 2:
                queue.put(("Not yet implemented", channel))
                return

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
