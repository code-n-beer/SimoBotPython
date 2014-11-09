import time
import socket
import sys
import ConfigParser

import glob
import os

import select

import inspect

#import Features.uguuFeature
#from Features import *
import Features
from LightweightApi import SimoLightweightApi

from multiprocessing import Process
from multiprocessing import Queue


print sys.version

configparser = ConfigParser.ConfigParser()
configparser.read("Resources/settings.cfg")

config = dict(configparser.items("connection"))

server = config['server']       #settings
channel = config['channel']
botnick = config['botnick']
username = config['username']
passwd = config['password']
port = int(config['port'])

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
print "connecting to:"+server
irc.connect((server, port))                                                         #connects to the server
irc.send("USER "+ username +" "+ botnick +" "+ botnick +" :VarjoSimo\n") #user authentication
irc.send("NICK "+ botnick +"\n")                            #sets nick
#irc.send("PRIVMSG nickserv :iNOOPE\r\n")    #auth
irc.send("PASS " + passwd + "\n")
irc.send("JOIN "+ channel +"\n")        #join the chan

q = Queue()
pongQueue = Queue()


#print Features.uguuFeature
commands = {}
modules = []

#print classes

def loadFeatures():
    classes = inspect.getmembers(sys.modules["Features"], inspect.isclass)
    for featureName, featureClass in classes:
        feature = featureClass();
        for cmd in feature.cmdpairs:
            commands[cmd] = feature.cmdpairs[cmd]


loadFeatures()

print commands

# Start Simo Lightweight API
p = Process(target=SimoLightweightApi().execute, args=(commands,q,))
p.start()


def sendMsg(irc, message):
    msg, channel = message
    msg = msg.replace("\n","")
    msg = msg.replace("\r\n","")

    #encode msg with utf-8 if not already
    try:
        msg = msg.encode('utf-8')
    except UnicodeDecodeError:
        print "msg already utf-8"

    irc.send("PRIVMSG " + channel.encode('utf-8') + " :" + msg + "\r\n")

def sendPong(pong):
    irc.send(pong)


while 1:
    time.sleep(0.025)
    irc.setblocking(0)

    inputReady, outputReady, exceptr = select.select([irc],[irc],[])

    if outputReady:
        if not q.empty():
            result = q.get()
            #print "got result: " + result
            sendMsg(irc, result)
        if not pongQueue.empty():
            sendPong(pongQueue.get())

    if not inputReady:
        #print "not ready"
        continue

    print "ready"

    text=irc.recv(2048)  #receive the text


    if(text.strip() == ""):
        continue;

    print text

    try:
        text = text.decode('utf-8')
        print "was utf8"
    except UnicodeDecodeError:
        text = text.decode('latin-1')
        print "was latin"

    #print type(text)

    if text.find('PING') != -1:                          #check if 'PING' is found
        #irc.send() #returns 'PONG'
        pong = 'PONG ' + text.split() [1] + '\r\n'
        pongQueue.put(pong)
        continue;

    print text   #print text to console

    msgSplit = text.split(':')
    nick = msgSplit[1].split("!")[0]
    msg = ":".join(msgSplit[2:])
    channel = text.split()[2]

    print nick + ": " + msg;

    if msg.startswith("!reload"):
        #sendMsg(irc,channel,"reload")
        #reloadModules(modules)
        reload(Features)
        loadFeatures()

        print "Reloaded features"

        #loadFeatures(False)
        #reload(Features)
        #irc.send("PRIVMSG " + channel + " :sis t. varjosimo\r\n");

    if "http" in msg or "www" in msg:
        print "dispatching urltitle"
        p = Process(target=commands["http"], args=(q, nick, msg, channel))
        p.start()

    stringdes = msg.split()
    if len(stringdes) < 1:
        continue

    cmd = msg.split()[0]
    if cmd in commands.keys():
        print "dispatching " + cmd
        p = Process(target=commands[cmd], args=(q, nick, msg, channel))
        p.start()

    #if msg.startswith("!varjouguu"):
    #    p = Process(target=uguuExecute,args=(q, msg))
    #    p.start()


