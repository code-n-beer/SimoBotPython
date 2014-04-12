from urllib import urlencode
import urllib2
import json
import ConfigParser, os

class reittiopasFeature:

    reittiopasApiURI = "http://api.reittiopas.fi/hsl/prod/"
    config = ConfigParser.ConfigParser()
    config.read("Resources/settings.cfg")
    username = config.get('reittiopas','user')
    password = config.get('reittiopas','pass')

    def __init__(self):
        self.cmdpairs = {
                "!reittiopas" : self.execute
                }

    def call(self, **params):
        for key,val in params.items():
            if val is None:
                del params[key]
            if isinstance(val, str):
                params[key] = val.decode("utf-8")
            if isinstance(val, unicode):
                params[key] = val.encode("utf-8")

        #Build url for API call
        fetch_url = (self.reittiopasApiURI
                    + "?" + urlencode(params)
                    + "&"
                    + "user=%s&pass=%s" % (self.username, self.password))

        try:
            resp = None
            resp = urllib2.urlopen(fetch_url)
            body = resp.read()
        except urllib2.URLError, e:
            print "API call failed: " + e.reason
            return
        finally:
            if resp:
                resp.close()

        return body

    def callForJSON(self, **params):
        body = self.call(format="json", **params)
        js = json.loads(body)
        return js

    def callGeocode(self, location):
        return self.callForJSON(request="geocode", key=location)

    def callRoute(self, **params):
        return self.callForJSON(request="route", **params)

    def formatTime(self, time):
        return time[-4:-2]+":"+time[-2:] #YYYYMMDDHHMM

    def formatCode(self, code):
        if code[:3] == "300":    #local train
            return code[4]
        elif code[:4] == "1300": #metro V for Vuosaari, M for Mellunmaki
            return code[4]
        elif code[:4] == "1019": #Suomenlinna ferry
            return "Suomenlinna"
        return code[1:-2].lstrip("0") #Regular line number

    def formatTransportTypeAndCode(self, code, type):
        types = {
                1: u"Bus",
                2: u"Tram",
                3: u"Bus",
                4: u"Bus",
                5: u"Bus",
                6: u"Metro",
                7: u"Ferry",
                8: u"Bus",
                12: u"Train",
                21: u"Bus",
                22: u"Bus",
                23: u"Bus",
                24: u"Bus",
                25: u"Bus",
                36: u"Bus",
                39: u"Bus",
            }
        return types[int(type)] + " " + self.formatCode(code).strip()

    def execute(self, queue, nick, msg, channel):
        locations = msg.split()
        if len(locations) != 3:
            print "Give start and destination"
            queue.put(("Give start and destination locations", channel))
            return

        start = self.callGeocode(locations[1])[0]['coords']
        destination = self.callGeocode(locations[2])[0]['coords']

        d = {'from':start, 'to':destination}
        route = self.callRoute(**d)

        depTime = self.formatTime(route[0][0]['legs'][0]['locs'][0]['depTime'])
        try:
            firstTransport = self.formatTransportTypeAndCode(
                    route[0][0]['legs'][1]['code'],
                    route[0][0]['legs'][1]['type'])
            firstTransportDepTime = self.formatTime(route[0][0]['legs'][1]['locs'][0]['depTime'])
            firstStopName = route[0][0]['legs'][1]['locs'][0]['name']
            result = "Leave at " + depTime + " to " + firstStopName + ", " + firstTransport + " arrives at " + firstTransportDepTime
        except IndexError:
            result = "Just walk"
        #Only shows first leg for now, if first leg is not found reittiopas suggests walking
        #Need to implement display for all legs
        queue.put((result, channel))
