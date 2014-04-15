# coding=utf-8
from urllib import urlencode
import urllib2
import json
import ConfigParser, os
import re

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
        try:
            js = json.loads(body)
        except ValueError, e:
            print e
            return
        return js

    def callGeocode(self, location):
        return self.callForJSON(request="geocode", key=location)

    def callRoute(self, **params):
        return self.callForJSON(request="route", show=1, **params)

    def formatTime(self, time):
        return time[-4:-2]+":"+time[-2:] #YYYYMMDDHHMM

    def formatLength(self, length):
        if length < 1000:
            return str(int(length)) + "m"
        return "%.1fkm" % (length/1000)

    def formatDuration(self, duration):
        return "%dmin" % (duration/60)

    def formatCode(self, code):
        if code[:3] == "300":    #local train
            return code[4]
        elif code[:4] == "1300": #metro V for Vuosaari, M for Mellunmaki
            if code [-1:] == "2":
                return u"Ruoholahti"
            elif code[4] == "M":
                return u"Mellunmäki"
            elif code[4] == "V":
                return u"Vuosaari"
            return ""
        elif code[:4] == "1019": #Suomenlinna ferry
            return u"Suomenlinna"
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

    def routeBuilder(self, route):
        legs = len(route[0][0]['legs'])

        #First leg for depTime
        routeStr = self.formatTime(route[0][0]['legs'][0]['locs'][0]['depTime']) + " > "
        #Transport legs
        for i in range(1, legs-1):
            if i%2 != 0:
                leg = (self.formatTransportTypeAndCode(
                        route[0][0]['legs'][i]['code'],
                        route[0][0]['legs'][i]['type'])
                        + " from " + route[0][0]['legs'][i]['locs'][0]['name']
                        + " @" + self.formatTime(route[0][0]['legs'][i]['locs'][0]['depTime']) + " > ")
                routeStr += leg

        #Last leg for arrival time and last stop
        lastStop = route[0][0]['legs'][legs-1]['locs'][0]['name']
        lastStopArrTime = route[0][0]['legs'][legs-1]['locs'][0]['arrTime']
        routeStr += lastStop + " @"+ self.formatTime(lastStopArrTime)
        arrival = len(route[0][0]['legs'][legs-1]['locs'])
        if arrival > 0:
            routeStr += " > Destination @" + self.formatTime(route[0][0]['legs'][legs-1]['locs'][arrival-1]['arrTime'])

        #Length and duration
        length = self.formatLength(route[0][0]['length'])
        duration = self.formatDuration(route[0][0]['duration'])
        routeStr += " | " + length + " " + duration
        return routeStr

    def execute(self, queue, nick, msg, channel):
        userInput = re.split('[,>-]', msg[12:])
        if len(userInput) < 2:
            print "Need at least start and destination"
            queue.put(("Give start and destination location separated with , - or >", channel))
            return

        try:
            start = self.callGeocode(userInput[0])[0]['coords']
        except TypeError:
            queue.put(("No location found for %s" %(userInput[0].strip()), channel))
            return
        try:
            destination = self.callGeocode(userInput[1])[0]['coords']
        except TypeError:
            queue.put(("No location found for %s" %(userInput[1].strip()), channel))
            return

        # Manual input for departure time
        try:
            time = userInput[2].strip()
            if len(time) == 5:
                time = "".join(re.split('[.:]', time))
            if len(time) == 4:
                if (0 <= int(time[:2]) < 24) and (0 <= int(time[2:]) < 60):
                    d = {'from':start, 'to':destination, 'time':str(time)}
            else:
                d = {'from':start, 'to':destination}
        except IndexError:
            d = {'from':start, 'to':destination}

        route = self.callRoute(**d)

        try:
            result = self.routeBuilder(route)
        except IndexError:
            result = "Just walk"
        print "executed reittiopas"
        queue.put((result, channel))
