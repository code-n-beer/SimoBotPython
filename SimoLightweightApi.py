# vim: set fileencoding=UTF-8 :
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
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
      request = request.split("=")
      message = request[1]
      message = urllib.unquote(message).strip()

      if (len(request) < 2 or (request[0] != 'command' and request[0] != 'say') or len(message) > 512
          or not self.server.regex.match(message)):
        self.wfile.write('')
        return
      
      if request[0] == 'say':
        print 'saying ' + request[1]
        self.server.ircQueue.put(("via api: " + request[1], "#simobot"))
        return

      command = None
      try:
        command = self.server.commands[message.split(" ")[0]]
      except LookupError:
        self.wfile.write('')
        return
      
      q = Queue()
      p = Process(target=command, args=(q, 'HttpApi', message, '#simobot'))
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

  def execute(self, commands, queue, port=8888):
    serverAddress = ('localhost', port)
    httpd = self.Server(serverAddress, self.Handler, commands, queue)
    print 'Starting http server...'
    httpd.serve_forever()



