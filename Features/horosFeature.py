# vim: set fileencoding=UTF-8 :
import urllib2
import datetime

class horosFeature:

    def __init__(self):
        self.cmdpairs = {
                "!horos" : self.execute
                }
        self.horokset = {"oinas": "aries", "härkä".decode('utf-8'): "taurus", "harka": "taurus", "kaksoset": "gemini", "rapu": "cancer", "leijona": "leo", "neitsyt": "virgo", "vaaka": "libra", "skorpioni": "scorpion", "jousimies": "sagittarius", "kauris": "capricorn", "vesimies": "aquarius", "kalat": "pisces" }


    def execute(self, queue, nick, msg, channel):
        msg = msg.split()

        if len(msg) < 2:
          queue.put(("supply me with your sign", channel))
          return

        msg = msg[1].rstrip()
        horosName = self.horokset.get(msg,0)
        if not horosName:
            queue.put(("not a valid sign", channel))
            return
        try:
            horos = urllib2.urlopen("http://www.astro.fi/future/weeklyForecast/sign/" + horosName).read()
        except urllib2.URLError, e:
            print "fetching horos failed: " + e.reason
            queue.put(("fetching horos failed: " + e.reason, channel))
            return

        horos = horos.decode('utf-8')
        horos = self.dropHtmlPrecedingHoroscope(horos,msg)
        horos = self.dropHtmlTailingHoroscope(horos)
        horos = self.html2Txt(horos)

        print horos
        queue.put((horos, channel))


    def dropHtmlPrecedingHoroscope(self, html, sign):
        sign = sign[1:]
        tagCount = datetime.datetime.today().weekday() + 1

        htmlArray = html.split(sign + "</h3><p>", tagCount + 1)
        result = htmlArray[tagCount]

        if (not result) or len(result) < 20:
            return "failed to parse HTML (horoscope too short)"

        return result

    def dropHtmlTailingHoroscope(self, html):
        html = html.split("<br />", 1)
        result = html[0]
        if "</p>" in result:
            result = html[:-4]

        if not result or len(result) > 500:
            return "failed to parse HTML (horoscope too long)"

        return result


    def html2Txt(self, html):
        html = html.encode('utf-8')
        html = html.replace("&auml;", "ä")
        html = html.replace("&ouml;", "ö")
        html = html.replace("&Auml;", "Ä")
        html = html.replace("&Ouml;", "Ö")
        return html
