# coding=utf8
from eventregistry import *
from datetime import *
import random
import pickle
import os 

class someFeature:
    def __init__(self):
        self.cmdpairs = {
                "!some" : self.execute,
                }
        self.er = EventRegistry()

    def execute(self, queue, nick, msg, channel):
        now = datetime.now()
        dateString = '{:%Y-%m-%d}'.format(now)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        somefile = None
        mostSharedArticles = {}
        try:
            somefile = open(dir_path + '/.some.tmp', 'rb')
            mostSharedArticles = pickle.load(somefile)
            somefile.close()
        except IOError:
            print "IOERROR while opening .some.tmp, ignoring"
            pass

        if not mostSharedArticles or now - timedelta(days = 1) > mostSharedArticles['lastFetch']:
            q = GetTopSharedArticles(date = dateString, count = 30)
            res = self.er.execQuery(q)
            if res[dateString]:
                mostSharedArticles['articles'] = res[dateString]
                mostSharedArticles['lastFetch'] = now

        article = mostSharedArticles['articles'].pop(random.randint(0, len(mostSharedArticles['articles']) - 1))
        articleBody = article['body'].split("\n")[0]

        queue.put((articleBody, channel))

        somefile = open(dir_path + '/.some.tmp', 'wb')
        pickle.dump(mostSharedArticles, somefile)
        somefile.close()
