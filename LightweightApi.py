# vim: set fileencoding=UTF-8 :
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import SocketServer
import re
import time
from multiprocessing import Process
from multiprocessing import Queue
import urllib2 as urllib

class SimoLightweightApi:

  class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
      self.send_response(200)
      self.send_header('Content-Type', 'text/plain')
      self.send_header('Content-Encoding', 'UTF-8')
      self.end_headers()

    def do_GET(self):
      self._set_headers()
      self.wfile.write(self.server.motd)

    def do_HEAD(self):
      self._set_headers()

    def do_POST(self):
      self._set_headers()

      length = 0
      try:
        length = int(self.headers['Content-Length'])
      except Exception:
        self.wfile.write('')
        return
      request = self.rfile.read(length)
      print request
      print urlparse.parse_qs(request)

      request = urlparse.parse_qs(request)
      if not 'command' in request or not self.server.regex.match(request['command'][0]) \
          or len(request['command'][0]) > 510:
        self.wfile.write('')
        return
      message = urllib.unquote(request['command'][0]).strip()

      sender = 'HttpApi'
      if 'sender' in request and self.server.regex.match(request['sender'][0]) \
          and len(request['sender'][0]) <= 40:
        sender = urllib.unquote(request['sender'][0]).strip()
      
      commandStr = message.split(" ")[0]
      if "http" in message or "www" in message:
        commandStr = "http"

      command = None
      try:
        command = self.server.commands[commandStr]
      except LookupError:
        self.wfile.write('')
        return
      
      q = Queue()
      p = Process(target=command, args=(q, sender, message, '#simobot'))
      p.start()
      
      result = ""
      i = 0
      while i < 320:      # wait 8 seconds
        time.sleep(0.025)
        if not q.empty():
          result = q.get()[0]
          break
        i = i + 1

      try:
        result = result.encode('utf-8')
      except UnicodeDecodeError:
        print 'already in unicode'

      self.wfile.write(result)

  class Server(HTTPServer):
    def __init__(self, *args, **kw):
      HTTPServer.__init__(self, *args[:2], **kw)
      self.commands = args[2]
      self.ircQueue = args[3]
      self.regex = re.compile('^[A-Öa-ö!-?_()+*.=/ ]+$')
      self.motd = """Usage: send command in POST key 'command', acquire Simo's reply in response
Remember to replace spaces with a +

This server returns empty content on error"""

  def execute(self, commands, queue, port=8889):
    serverAddress = ('localhost', port)
    httpd = self.Server(serverAddress, self.Handler, commands, queue)
    print 'Starting http server...'
    httpd.serve_forever()



