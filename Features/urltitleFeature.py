# vim: set fileencoding=UTF-8 :
import urllib2
from StringIO import StringIO
import gzip
from HTMLParser import HTMLParser

class urltitleFeature:

  def __init__(self):
      self.cmdpairs = {
              "http" : self.execute
              }

  def execute(self, queue, nick, msg, channel):
    response = None
    try:
      response = urllib2.urlopen(msg)
      if not response.info().get('Content-Type').startswith('text/html'):
        return
      if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        response = gzip.GzipFile(fileobj=buf)
    except urllib2.URLError, e:
        return

    parser = titleParser()
    parser.feed(response.read())

    print parser.title
    queue.put(("".join(parser.title), channel))
    

class titleParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.record = 0
    self.title = []

  def handle_starttag(self, tag, attrs):
    if tag == 'title':
      self.record = 1

  def handle_endtag(self, tag):
    self.record = 0

  def handle_data(self, data):
    if self.record:
      self.title.append(data.decode('utf-8'))
