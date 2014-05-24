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
    url = self.findUrl(msg)

    response = None
    try:
      response = urllib2.urlopen(url)
      contentType = response.info().get('Content-Type')
      if not (contentType.startswith('text/html') or 'xml' in contentType):
        print 'unknown content'
        return
      if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        response = gzip.GzipFile(fileobj=buf)
    except urllib2.URLError, e:
        print 'urrlib error ' + e.reason
        return

    parser = titleParser()
    parser.feed(response.read())

    title = "".join(parser.title).strip()
    print parser.title
    queue.put((title, channel))

  def findUrl(self, msg):
    httpIndex = msg.find("http")

    if httpIndex == -1:
      httpIndex = msg.find("www")
    url = msg[httpIndex:].split(" ", 1)[0]

    if not url.startswith("http"):
      url = "http://" + url

    return url


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
