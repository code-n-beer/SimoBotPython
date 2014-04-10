import time
import socket
import sys

import glob
import os

import select

import inspect

#import Features.uguuFeature
#from Features import *
import Features

from multiprocessing import Process
from multiprocessing import Queue


print sys.version

server = "irc.nebula.fi"       #settings
channel = "#SimoBot"
botnick = "PizzaBot"
#username = "simobot"
passwd = "herpderp"
port = 6667

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
print "connecting to:"+server
irc.connect((server, port))                                                         #connects to the server
irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :VarjoSimo\n") #user authentication
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

def sendMsg(irc, message):
    msg, channel = message
    msg = msg.replace("\n","");
    msg = msg.replace("\r\n","");
    irc.send("PRIVMSG " + channel.encode('utf-8') + " :" + msg.encode('utf-8') + "\r\n");

def sendPong(pong):
    irc.send(pong)


while 1:    #puts it in a loop
    time.sleep(0.025)
    irc.setblocking(0)

    inputr, outputr, exceptr = select.select([irc],[irc],[])

    if outputr:
        if not q.empty():
            result = q.get()
            #print "got result: " + result
            sendMsg(irc, result)
        if not pongQueue.empty():
            sendPong(pongQueue.get())

    if not inputr:
        #print "not ready"
        continue

    print "ready"

    text=irc.recv(2048)  #receive the text


    if(text.strip() == ""):
        continue;

    print text

    text = text.decode('utf-8')

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

    if "!reload" in msg:
        #sendMsg(irc,channel,"reload")
        #reloadModules(modules)
        reload(Features)
        loadFeatures()

        #loadFeatures(False)
        #reload(Features)
        #irc.send("PRIVMSG " + channel + " :sis t. varjosimo\r\n");

    cmd = msg.split()[0]
    if cmd in commands.keys():
        print "dispatching " + cmd
        p = Process(target=commands[cmd], args=(q, nick, msg, channel))
        p.start()

    #if msg.startswith("!varjouguu"):
    #    p = Process(target=uguuExecute,args=(q, msg))
    #    p.start()


