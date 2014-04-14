import pycurl, json, StringIO, sys, redis
import random

def getJsonFromImage(url, port):
    filen = url
    data = json.dumps({"image_url": filen})
    url = 'http://localhost/search'

    storage = StringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.URL, str(url))
    c.setopt(c.PORT, int(port))
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, data)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()

    returned_json = storage.getvalue()
    return returned_json
    #print returned_json

class imageTagFeature:

    def __init__(self):
        self.cmdpairs = {
                "!pic" : self.executePic
                }

    def executePic(self, queue, nick, msg, channel):
        r = redis.StrictRedis(host='localhost', port=6381, db=0)

        #print r.srandmember(

        splits = msg.split()
        pics = []
        if len(splits) < 2:
            key = r.randomkey()
            pics = r.smembers(key)
            pics = list(pics)
        else:
            picture = msg.split()[1]
            key = msg.split()[1]
            pictures = r.smembers(picture)
            pics = list(pictures)

        count = len(pics)
        print count
        if count == 1:
            pic = pics[0]
            randomIdx = 0
        elif count < 1:
           queue.put(("Not found", channel))
        else:
            randomIdx = random.randint(0,count - 1)
            pic = pics[randomIdx]

        pic = key + ": " + pic + " [" + str(randomIdx + 1) + "/" + str(count) + "]"
        queue.put((pic, channel))

    def executeGetPicJSON(self, queue, nick, msg, channel):
        url = msg.split()[1:]
        try:
            getJsonFromImage(url, 5000)
        except:
            print "getting pic json failed"
        #print "ses"
