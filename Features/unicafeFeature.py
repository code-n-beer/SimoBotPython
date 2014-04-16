# vim: set fileencoding=UTF-8 :
import urllib2
import xml.etree.ElementTree as ET
import datetime
import re

class unicafeFeature:

    def __init__(self):
        self.cmdpairs = {
                "!varjouc" : self.execute
                }

    def execute(self, queue, nick, msg, channel):
      menuExa = ""
      menuChem = ""
      try:
        menuExa = urllib2.urlopen("http://www.hyyravintolat.fi/rss/fin/11/").read()
        menuChem = urllib2.urlopen("http://www.hyyravintolat.fi/rss/fin/10/").read()
      except urllib2.URLError, e:
          print "fetching menu failed: " + e.reason
          queue.put(("fetching menu failed: " + e.reason, channel))
          return
        
      today = datetime.datetime.today().weekday() 

      exaLunch = self.parseRSSString(menuExa, "Exactum", today)
      chemLunch = self.parseRSSString(menuChem, "Chemicum", today)
      result = exaLunch + " /::/ " + chemLunch

      # vittuun ne päivän hedelmät
      result = re.sub(r' \( .* \)$','',result)

      print result
      queue.put((result, channel))

    def parseRSSString(self, menuRSS, restaurant, today):
      root = ET.fromstring(menuRSS)
      root = root.findall("./channel/item/description")

      result = "no lunch today"
      if today < len(root):
        tmpstring = "<root>" + root[today].text.encode('utf-8').replace(">,",">") + "</root>"
        todaysMenu = ET.XML(tmpstring)
        todaysPrices = todaysMenu.findall(".p/span[@class='priceinfo']")
        todaysMenu = todaysMenu.findall("./p/span[@class='meal']")

        result = self.generateMenuString(todaysMenu, todaysPrices)

      result = restaurant + ": "+result
      return result

    
    def generateMenuString(self, todaysMenu, todaysPrices):
      # tän vois tehdä nätimmin
      todaysMenuStrings = []
      i = 0
      for menu in todaysMenu:
        menuString = menu.text.lower().capitalize()
        if i < len(todaysPrices) and "Maukkaasti" in todaysPrices[i].text:
          menuString += " [M]"
        todaysMenuStrings.append(menuString)
        i = i + 1
          
      return " // ".join(todaysMenuStrings)

    def html2Txt(self, html):
        html = html.encode('utf-8')
        html = html.replace("&auml;", "ä")
        html = html.replace("&ouml;", "ö")
        html = html.replace("&Auml;", "Ä")
        html = html.replace("&Ouml;", "Ö")
        return html
