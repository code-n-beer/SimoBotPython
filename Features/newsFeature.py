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
        self.newsSites = {"http://www.magneettimedia.com/feed/":"[",
            "http://feeds.feedburner.com/stara/ilman-big-brotheria?format=xml":"[",
            "http://tuima.fi/?feed=rss2":"&#8230;",
            "http://www.iltalehti.fi/rss/kotimaa.xml":"[",
            "http://feeds.feedburner.com/findancecom/uutiset/maailmalta?format=xml":"["}


    def execute(self, queue, nick, msg, channel):
        
      today = datetime.datetime.today().weekday() 

      if not self.newsStrings:
        self.newsStrings = self.fetchNews(queue, channel)

      news = self.newsStrings.pop()
      print news
      queue.put((news, channel))
      self.seenNews.append(news)
      

    def fetchNews(self, queue, channel):
      newsStrings = []
      for url in self.newsSites.keys():
        feed = self.fetchUrlToString(url)
        self.parseFeedString(feed, newsStrings, self.newsSites[url])

      shuffle(newsStrings)

      return newsStrings
      

    def parseFeedString(self, magnfeed, newsStrings, EOL="["):
      root = ET.fromstring(magnfeed)
      items = root.findall("./channel/item")

      for news in items:
        title = news.find("./title").text
        description = news.find("./description").text
        
        # concat title and description, remove tail from description, strip whitespace
        news = (title.strip() + " // " + description.split(EOL)[0].strip()).encode('utf-8')
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
