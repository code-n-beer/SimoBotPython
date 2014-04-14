import json
from Features.getTagsForImageFeature import *
import re
from operator import itemgetter
import sys
import redis
import threading

blacklisted = [line.strip() for line in open('Resources/blacklistedtags.txt')]
#jsondata = getJsonFromImage(picture)

wordCounts = {}
files = []

folder = sys.argv[1] #Target folder from where to find all pictures
threadCount = int(sys.argv[2]) #How many threads to use

def stripStuff(string):
    string = string.lower()
    string = re.sub(r'\W+', '', string)
    string = re.sub(r'\d+', '', string)
    if string.startswith("http"):
        string = ""
    if string in blacklisted:
        string = ""
    return string

def getAndAddWords(dictionary, string):
    words = string.split()
    for word in words:
        #theword = word.lower()
        theword = stripStuff(word)
        if len(theword) < 3:
            continue
        if theword in dictionary:
            dictionary[theword] = dictionary[theword] + 1
        else:
            dictionary[theword] = 1
    return dictionary

def pumpToRedis(dictionary, picture):
    r = redis.StrictRedis(host='localhost', port=6381, db=0)
    x = 0
    while x < 5:
        #print dictionary
        try:
            key = dictionary[x][0]
        except IndexError:
            x += 1
            continue
        value = picture
        if r.sismember(key, value):
            print value + " not added to " + key
            x += 1
            continue
        r.sadd(key, picture)
        print key + ": " + picture
        x += 1

    print ""
    print ""

def runTagGetAndPumpToRedis(url, threadIndex):
    picture = url


    #oh my fucking god this is disgusting. But I can't bother to make someone else's server multithreaded
    #so I'll run it on multiple singlethreaded servers >_>
    port = "500"
    portWithIdx = port + str(threadIndex)
    actualPort = str(portWithIdx)


    try:
        jsondata = getJsonFromImage(picture, actualPort)
        stuff = json.loads(jsondata)
    except:
        return

    wordCounts = {}

    for key in stuff.keys():
        #print key
        #print stuff[key]
        words = stuff[key]
        for idx in words:
            wordCounts = getAndAddWords(wordCounts, idx)

    sortedCounts = sorted(wordCounts.items(), key=itemgetter(1), reverse=True)
    pumpToRedis(sortedCounts, picture)

def fileToURL(filename):
    return "http://tsarpf.datisbox.net/kuvei/" + filename

def runThread(files, idx):
    while len(files) > 0:
        targetFile = files.pop()
        targetURL = fileToURL(targetFile)
        runTagGetAndPumpToRedis(targetURL, idx)

def distributedGet(files):
    picturesUnevenCount = int(len(files) / threadCount)
    picturesLeftOver = len(files) %  threadCount

    picturesPerThread = [picturesUnevenCount] *  threadCount #[0] * 10 == [0,0,0,0,0]

    for x in range(0, picturesLeftOver):
       picturesPerThread[x] += 1

    threads = []
    for x in range(0, threadCount):

        #filesForThread = []
        #for y in range(0,picturesPerThread[x]):
        #    filesForThread.append(files.pop())

        #Why doesn't this work? :(... it does?
        filesForThread = files[-picturesPerThread[x]:]
        del files[-picturesPerThread[x]:]

        print filesForThread[0]
        #print files[0]
        thread = threading.Thread(target=runThread, args=(filesForThread, x, ))
        thread.start()
        threads.append(thread)

    while len(threads) > 0:
        threads.pop().join()

#def run(folder="~/public_html/kuvei/"):
def getFiles(folder):
    import glob
    import os
    files = []
    for file in os.listdir(folder):
        files.append(file)

    files = files[::-1]
    return files

def run(folder):
    files = getFiles(folder)
    distributedGet(files)

run(folder)








#def threadedGet(files) #A better version would give a thread a list of pictures to load and let it do it's job
#    threads = []
#    while len(files) > 0:
#        targetFile = files.pop()
#        targetURL = fileToUrl(targetFile)
#
#        thread = threading.Thread(target=runTagGetAndPumpToRedis, args=(targetURL))
#
#        threads.append(thread)
#
#        if len(threads) >= threadCount:
#            #for x in range(0,threadCount):
#            while len(threads) > 0
#                threads.pop().join()












#print ses


