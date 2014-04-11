import urllib2

class horosFeature:
    horokset = {"oinas": "aries", "härkä": "taurus", "harka": "taurus", "kaksoset": "gemini", "rapu": "cancer", "leijona": "leo", "neitsyt": "virgo", "vaaka": "libra", "skorpioni": "scorpion", "jousimies": "sagittarius", "kauris": "capricorn", "vesimies": "aquarius", "kalat": "pisces" }

    def __init__(self):
        self.cmdpairs = {
                "!varjohoros" : self.execute
                }


    def execute(self, queue, nick, msg, channel):
        horosName = horokset[msg]
        if !horosName:
            queue.put("why won't you give me a sign~", channel)
            return
        try:
            horos = urllib2.urlopen("http://www.astro.fi/future/weeklyForecast/sign/" + horosName).read()
        except urllib2.URLError, e:
            print "fetching horos failed: " + e.reason
            queue.put(("fetching horos failed: " + e.reason, channel))
            return
        print "fetched horos"

        horos = dropHtmlPrecedingHoroscope(horos,msg)
        horos = dropHtmlTailingHoroscope(result)
        horos = html2Txt(horos)

        print horos
        queue.put((horos, channel))


    def dropHtmlPrecedingHoroscope(html, sign):
        sign = sign[1:]
        tagCount = 2

        if tagCount > 14 || tagCount < 2:
            return "invalid date"

        htmlArray = html.split(sign + "</h3><p>", tagCount + 1)
        result = htmlArray[tagCount]

        if !result || len(result) < 20:
            return "failed to parse HTML (horoscope too short)"

        return result

    def dropHtmlTailingHoroscope(html):
        html = html.split("<br />", 1)
        result = html[0]

        if !result || len(result) > 500:
            return "failed to parse HTML (horoscope too long)"

        return result


    def html2Txt(html):
        html = html.replace("&auml;", "ä")
        html = html.replace("&ouml;", "ö")
        html = html.replace("&Auml;", "Ä")
        html = html.replace("&Ouml;", "Ö")
        return html
