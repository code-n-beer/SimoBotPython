import gensim 

class word2vecFeature:

    def __init__(self):
       self.cmdpairs = {
           "!similar": self.execute,
           "!similarn": self.executen,
           "!likexytoz": self.executexyz
       }
       self.model = gensim.models.Word2Vec.load("./Resources/word2vec_2016-2019_04.model")

    def executexyz(self, queue, nick, msg, channel):
        words = msg.split()
        if len(words) < 4:
            print("nothing to similarize")
            return

        x = words[1]
        y = words[2]
        z = words[3]

        try:
            m = self.model.wv.most_similar (positive=[z, x], negative=[y])
        except(KeyError):
            queue.put(('Not found', channel))

        results = []
        for result in m:
            val, prob = result
            results.append(val)

        ret_val = u' '.join(results).encode('utf-8').strip()

        queue.put((ret_val, channel))

    def execute(self, queue, nick, msg, channel):
        words = msg.split()
        if len(words) < 2:
            print("nothing to similarize")
            return

        word = words[1]
        try:
            m = self.model.wv.most_similar (positive=word.lower())
        except(KeyError):
            queue.put((word + ' not found', channel))
        results = []
        for result in m:
            val, prob = result
            results.append(val)

        ret_val = u' '.join(results).encode('utf-8').strip()
        queue.put((ret_val, channel))

    def executen(self, queue, nick, msg, channel):
        words = msg.split()
        if len(words) < 2:
            print("nothing to similarize")
            return

        words = words[1:]
        results = []
        for word in words:
            try:
                m = self.model.wv.most_similar (positive=word.lower())[0][0]
                results.append(m)
            except(KeyError):
                results.append(word)

        ret_val = u' '.join(results).encode('utf-8').strip()
        queue.put((ret_val, channel))