# Usage !weather <LOCATION>
# If no location given, defaults to Helsinki

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

    # String output for windDirection
    def windDirection(self, degrees):
        if 0 <= degrees < 10:
            return "N"
        if 10 <= degrees < 33:
            return "NNE"
        if 33 <= degrees < 55:
            return "NE"
        if 55 <= degrees < 78:
            return "ENE"
        if 78 <= degrees < 100:
            return "E"
        if 100 <= degrees < 123:
            return "ESE"
        if 123 <= degrees < 145:
            return "SE"
        if 145 <= degrees < 168:
            return "SSE"
        if 168 <= degrees < 190:
            return "S"
        if 190 <= degrees < 213:
            return "SSW"
        if 213 <= degrees < 235:
            return "SW"
        if 235 <= degrees < 258:
            return "WSW"
        if 258 <= degrees < 280:
            return "W"
        if 280 <= degrees < 303:
            return "WNW"
        if 303 <= degrees < 325:
            return "NW"
        if 325 <= degrees < 348:
            return "NNW"
        if 348 <= degrees <= 360:
            return "N"

        return

    def execute(self, queue, nick, msg, channel):
        # If no location is given, defaults to Helsinki
        if len(msg.split()) < 2:
            print "no location given for weather, defaulting to Helsinki"
            city = "Helsinki"
        else:
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

        windDirection = self.windDirection(windDirection)

        weather = location + ": " + str(temp) + u'\u00B0' + "C (" + str(tempMin) + "-" + str(tempMax) + u'\u00B0' + "C), " + str(windSpeed) + "m/s from " + windDirection + ", " + description

        print "executed weather"
        queue.put((weather, channel))
