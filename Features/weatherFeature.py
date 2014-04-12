import urllib2
import json

class weatherFeature:
    apiURI = "http://api.openweathermap.org/data/2.5/find?units=metric&q="

    def __init__(self):
        self.cmdpairs = {
                "!weather" : self.execute
                }

    def call(self, city):
        fetch_url = self.apiURI + city.strip()

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

    def callForJSON(self, city):
        body = self.call(city)
        js = json.loads(body)
        return js

    #Cant use range as key
    #def windDirection(self, degrees):
    #    directions = {
    #        range(1,10): u"N",
    #        range(11,33): u"NNE",
    #        range(34,55): u"NE",
    #        range(56,78): u"ENE",
    #        range(79,100): u"E",
    #        range(101,123): u"ESE",
    #        range(124,145): u"SE",
    #        range(146,168): u"SSE",
    #        range(169,190): u"S",
    #        range(191,213): u"SSW",
    #        range(214,235): u"SW",
    #        range(236,258): u"WSW",
    #        range(259,280): u"W",
    #        range(281,303): u"WNW",
    #        range(304,325): u"NW",
    #        range(326,348): u"NNW",
    #        range(349,360): u"N",
    #        }
    #    return directions[int(degrees)]

    def execute(self, queue, nick, msg, channel):
        if len(msg.split()) < 2:
            queue.put(("Give a location", channel))
            print "no location given for weather"
            return

        city = "%20".join(msg.split()[1:])
        js = self.callForJSON(city.encode("utf-8"))

        if js['count'] < 1:
            queue.put(("No data found", channel))
            return

        temp = js['list'][0]['main']['temp']
        tempMin = js['list'][0]['main']['temp_min']
        tempMax = js['list'][0]['main']['temp_max']
        windSpeed = js['list'][0]['wind']['speed']
        windDirection = js['list'][0]['wind']['deg']
        description = js['list'][0]['weather'][0]['description']
        location = js['list'][0]['name']

        weather = location + ": " + str(temp) + u'\u00B0' + "C (" + str(tempMin) + "-" + str(tempMax) + u'\u00B0' + "C), " + str(windSpeed) + "m/s from " + str(windDirection) + ", " + description

        print "executed weather"
        queue.put((weather, channel))
