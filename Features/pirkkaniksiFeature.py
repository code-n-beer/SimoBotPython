import urllib2

class pirkkaniksiFeature:

    def __init__(self):
        self.cmdpairs = {
                "!niksi" : self.execute
                }

    def execute(self, queue, nick, msg, channel):
        try:
            niksi = urllib2.urlopen("http://thermopylas.fi/ws/nicksit.php").read()
        except urllib2.URLError, e:
            print "niksi failed: " + e.reason
            queue.put(("niksi failed: " + e.reason, channel))
            return
        print "executed niksi"
        queue.put((niksi, channel))
