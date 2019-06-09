import gensim 
from gensim.models import KeyedVectors
import random

class word2vecFeature:

    def __init__(self):
       self.cmdpairs = {
           "!similar": self.execute_cnb,
           "!similaryle": self.execute_yle,

           "!similarn": self.execute_n_cnb,
           "!similarnyle": self.execute_n_yle,

           "!similarnr": self.execute_n_cnb_r,
           "!similarnyler": self.execute_n_yle_r,

           "!xminusyplusz": self.execute_xyz_cnb,
           "!xminusypluszyle": self.execute_xyz_yle,
#            "!xminusyplusz": self.execute_x_minus_y_plus_z
       }
       #self.cnb_wv = KeyedVectors.load_word2vec_format("./Resources/word2vec_2014-2019_04.model", limit=1000, binary=False)
       #self.cnb_wv = KeyedVectors.load("./Resources/word2vec_2014-2019_04.model")
       #self.cnb_wv.wv.save_word2vec_format('./Resources/w2v_cnb'+".bin", binary=True)
       
       self.yle_wv = KeyedVectors.load_word2vec_format("./Resources/w2v_yle.bin", limit=150000, binary=True)
       self.cnb_wv = KeyedVectors.load_word2vec_format("./Resources/w2v_cnb.bin", limit=150000, binary=True)

    #def x_plus_y(self, x, y):
    #    return self.model.wv.get_vector(x) + self.model.wv.get_vector(y)
    
    #def x_minus_y(self, x, y):
    #    return self.model.wv.get_vector(x) - self.model.wv.get_vector(y)
    #    
    #def x_minus_y_plus_z(self, x, y, z):
    #    return self.model.wv.similar_by_vector(
    #        self.x_plus_y(self.x_minus_y(x, y), z))

    #def x_plus_y_minus_z(self, x, y, z):
    #    return self.model.wv.similar_by_vector(
    #    self.x_minus_y(self.x_plus_y(x, y), z))
    #def x_plus_y_plus_z(self, x, y, z):
    #    return self.x_plus_y(self.x_plus_y(x, y), z)
    #def x_minus_y_minus_z(self, x, y, z):
    #    return self.x_minus_y(self.x_minus_y(x, y), z)
    #def execute_x_minus_y_plus_z(self, queue, nick, msg, channel):
    #    words = msg.split()
    #    if len(words) < 4:
    #        print("nothing to similarize")
    #        return

    #    x = words[1]
    #    y = words[2]
    #    z = words[3]

    #    results = []
    #    try:
    #        m = self.x_minus_y_plus_z(x,y,z)
    #        for word, _ in m:
    #            if word != x and word != y and word != z:
    #                results.append(word)
    #    except(KeyError):
    #        results.append('not found')

    #    ret_val = u' '.join(results).encode('utf-8').strip()
    #    queue.put((ret_val, channel))

    def execute_xyz_cnb(self, queue, nick, msg, channel):
        self.executexyz(queue, nick, msg, channel, self.cnb_wv)

    def execute_xyz_yle(self, queue, nick, msg, channel):
        self.executexyz(queue, nick, msg, channel, self.yle_wv)

    def executexyz(self, queue, nick, msg, channel, wv):
        words = msg.split()
        if len(words) < 4:
            queue.put(('nothing to similarize', channel))
            return

        x = words[1]
        y = words[2]
        z = words[3]

        try:
            m = wv.most_similar (positive=[z, x], negative=[y])
        except(KeyError):
            queue.put(('Not found', channel))

        results = []
        for result in m:
            val, _ = result
            results.append(val)

        ret_val = u' '.join(results).encode('utf-8').strip()

        queue.put((ret_val, channel))
    
    def execute_cnb(self, queue, nick, msg, channel):
        self.execute(queue, nick, msg, channel, self.cnb_wv)

    def execute_yle(self, queue, nick, msg, channel):
        self.execute(queue, nick, msg, channel, self.yle_wv)

    def get_m(self, wv, word):
        word = word.lower()
        return wv.most_similar (positive=word)

    def execute(self, queue, nick, msg, channel, wv):
        words = msg.split()
        if len(words) < 2:
            print("nothing to similarize")
            return
        if len(words) > 2:
            queue.put(('only one argument please, use similarn for many', channel))

        word = words[1]
        try:
            m = self.get_m(wv, word)
        except(KeyError):
            queue.put((word + ' not found', channel))
        results = []
        for result in m:
            val, _ = result
            results.append(val)

        ret_val = u' '.join(results).encode('utf-8').strip()
        queue.put((ret_val, channel))

    def execute_n_cnb(self, queue, nick, msg, channel):
        self.execute_n(queue, nick, msg, channel, self.cnb_wv)

    def execute_n_yle(self, queue, nick, msg, channel):
        self.execute_n(queue, nick, msg, channel, self.yle_wv)

    def execute_n(self, queue, nick, msg, channel, wv):
        words = msg.split()
        if len(words) < 2:
            print("nothing to similarize")
            return

        words = words[1:]
        results = []
        for word in words:
            try:
                m = wv.most_similar (positive=word.lower())[0][0]
                results.append(m)
            except(KeyError):
                results.append(word)

        ret_val = u' '.join(results).encode('utf-8').strip()
        queue.put((ret_val, channel))

    def execute_n_cnb_r(self, queue, nick, msg, channel):
        self.execute_n_r(queue, nick, msg, channel, self.cnb_wv)

    def execute_n_yle_r(self, queue, nick, msg, channel):
        self.execute_n_r(queue, nick, msg, channel, self.yle_wv)

    def get_top(self, results):
        top_p = results[0][1]
        p = top_p
        top_5p = []
        idx = 0
        while p > top_p - 0.10 and idx < len(results):
            top_5p.append(results[idx])
            p = results[idx][1]
            #print(p)
            idx+=1

        if len(top_5p) < 20:
            return results[:20]
        return top_5p

    def execute_n_r(self, queue, nick, msg, channel, wv):
        words = msg.split()
        if len(words) < 2:
            print("nothing to similarize")
            return

        words = words[1:]
        results = []
        for word in words:
            try:
                #m = wv.most_similar (positive=word.lower())
                m = wv.most_similar (positive=word.lower(), topn=100)
                tops = self.get_top(m)
                top = random.choice(tops)
                #print(word + " ".join(x[0] for x in tops))
                results.append(top[0])
            except(KeyError):
                results.append(word)

        ret_val = u' '.join(results).encode('utf-8').strip()
        queue.put((ret_val, channel))
