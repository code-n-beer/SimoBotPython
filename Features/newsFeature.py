# vim: set fileencoding=UTF-8 :
import urllib2
import xml.etree.ElementTree as ET
import datetime
from random import shuffle

class newsFeature:

    def __init__(self):
        self.cmdpairs = {
                "!news" : self.execute
                }
        self.seenNews = []
        self.newsStrings = []
        self.maxMessageLength = 478


    def execute(self, queue, nick, msg, channel):
        
      today = datetime.datetime.today().weekday() 

      if not self.newsStrings:
        self.newsStrings = self.fetchNews(queue, channel)

      news = self.newsStrings.pop()
      print news
      queue.put((news, channel))
      self.seenNews.append(news)
      

    def fetchNews(self, queue, channel):
      magnfeed = self.fetchUrlToString("http://www.magneettimedia.com/feed/") 
      starafeed = self.fetchUrlToString("http://feeds.feedburner.com/stara/ilman-big-brotheria?format=xml")
      tuimafeed = self.fetchUrlToString("http://tuima.fi/?feed=rss2")

      newsStrings = []
      self.parseFeedString(magnfeed, newsStrings)
      self.parseFeedString(starafeed, newsStrings)
      self.parseFeedString(tuimafeed, newsStrings, "&#8230;")
      shuffle(newsStrings)

      return newsStrings
      

    def parseFeedString(self, magnfeed, newsStrings, EOL="["):
      root = ET.fromstring(magnfeed)
      items = root.findall("./channel/item")

      for news in items:
        title = news.find("./title").text
        description = news.find("./description").text
        
        # concat title and description, remove tail from description
        news = (title + " // " + description.split(EOL)[0]).encode('utf-8')
        news = self.limitNewsToMaxMessageLength(news)
        news = self.magicLocaleFix(news)
        
        newsStrings.append(news)

    def limitNewsToMaxMessageLength(self, news):
      lastSentenceIndex = news.rfind(".", 0, self.maxMessageLength)
      return news[:lastSentenceIndex + 1]


    def fetchUrlToString(self, URL):
      string = ""
      try:
        string = urllib2.urlopen(URL).read()
      except urllib2.URLError, e:
          print "fetching news failed: " + e.reason
          queue.put(("fetching news failed: " + e.reason, channel))
          return
      print "fetched news"
      return string


    def html2Txt(self, html):
        html = html.encode('utf-8')
        html = html.replace("&auml;", "ä")
        html = html.replace("&ouml;", "ö")
        html = html.replace("&Auml;", "Ä")
        html = html.replace("&Ouml;", "Ö")
        return html
    
    def magicLocaleFix(self, string):
      string = string.replace("Ã¶", "ö")
      string = string.replace("Ã¤", "ä")
      return string
