# vim: set fileencoding=UTF-8 :
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import re
import time
from multiprocessing import Process
from multiprocessing import Queue

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
      request = request.split("=")
      message = request[1]

      if (len(request) < 2 or request[0] != 'command' or len(message) > 512
          or not self.server.regex.match(message)):
        self.wfile.write('')
        return
      
      message = message.replace("+", " ")
      command = None
      try:
        command = self.server.commands[message.split(" ")[0]]
      except Exception:
        self.wfile.write('')
        return
      
      q = Queue()
      p = Process(target=command, args=(q, 'HttpApi', message, '#simobot'))
      p.start()
      
      result = ""
      i = 0
      while i < 200:      # wait 8 seconds
        time.sleep(0.025)
        if not q.empty():
          result = q.get()[0].encode('utf-8')
          break
        i = i + 1

      self.wfile.write(result)

  class Server(HTTPServer):
    def __init__(self, *args, **kw):
      HTTPServer.__init__(self, *args[:2], **kw)
      self.commands = args[2]
      self.regex = re.compile('^![A-Öa-ö!-?_()+*.=/]+$')
      self.motd = """Usage: send command in POST key 'command', acquire Simo's reply in response
Remember to replace spaces with a +

This server returns empty content on error"""

  def execute(self, commands, port=8888):
    serverAddress = ('localhost', port)
    httpd = self.Server(serverAddress, self.Handler, commands)
    print 'Starting http server...'
    httpd.serve_forever()



