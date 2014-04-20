# vim: set fileencoding=UTF-8 :
import urllib2
from StringIO import StringIO
import gzip
from HTMLParser import HTMLParser
from Features.lastfmFeature import lastfmFeature
from multiprocessing import Queue
import re

class drinkifyFeature:

  def __init__(self):
      self.cmdpairs = {
              "!drinkify" : self.execute
              }

  def execute(self, queue, nick, msg, channel):
    searchString = msg[10:].strip()

    if searchString == 'np':
      searchString = self.fetchNpArtistFromLastfm(nick, queue, channel)
      if not searchString:
        return

    searchString = searchString.replace(" ", "%20").encode('utf-8')
    print "Searching " + searchString

    drinkifyResult = ""
    try:
      response = urllib2.urlopen("http://drinkify.org/" + searchString)
      if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        response = gzip.GzipFile(fileobj=buf)
      drinkifyResult = response.read()
    except urllib2.URLError, e:
        print "fetching drink failed: " + e.reason
        queue.put(("fetching drink failed: " + e.reason, channel))
        return
    
    parser = drinkifyParser()
    parser.feed(drinkifyResult)

    result = self.combineResultStringFromDataArray(parser.data)
    
    print result

    queue.put((result, channel))

  def fetchNpArtistFromLastfm(self, nick, queue, channel):
    # this could be done in parallel, but there's really no point
    lastfm = lastfmFeature()
    response = Queue()
    lastfm.execute(response, nick, '!varjonp', '#simobot')
    lastfmString = response.get()[0]
    
    if lastfmString.find(': ') == -1:      # something's wrong
      queue.put((lastfmString, channel))
      return ""

    lastfmArtist = re.findall(r'^[^:]*: (.+) -.*', lastfmString)[0]
    return lastfmArtist
    
  def combineResultStringFromDataArray(self, data):
    drinkName = data.pop(0)
    instructions = data.pop().strip()
    instructions = re.sub(r'([ \n]+)', ' ', instructions)
    ingredients = ", ".join(data)
    return "\"%s\": %s. %s" %(drinkName, ingredients, instructions)


class drinkifyParser(HTMLParser):

  def __init__(self):
    HTMLParser.__init__(self)
    self.recordData = 0
    self.recipeFound = 0
    self.ingredientsFound = 0
    self.data = []

  def handle_starttag(self, tag, attrs):
    if tag == 'div' and ('id', 'recipeContent') in attrs:
        self.recipeFound = 1
        return
    
    if self.recipeFound:
      if tag == 'h2':
        self.recordData = 1
        return
      if tag == 'ul' and ('class', 'recipe') in attrs:
        self.ingredientsFound = 1
        return

      if self.ingredientsFound:
        if tag == 'li':
          self.recordData = 1
          return
        if tag == 'p' and ('class', 'instructions') in attrs:
          self.recordData = 1
          return

  def handle_endtag(self, tag):
    self.recordData = 0
    if tag == 'div':
      self.recipeFound = 0
      return

  def handle_data(self, data):
    if self.recordData:
      self.data.append(data)
