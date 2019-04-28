import gensim 

class word2vecFeature:

    def __init__(self):
       self.cmdpairs = {
           "!similar": self.execute
       }
       self.model = gensim.models.Word2Vec.load("./Resources/word2vec_2016-2019_04.model")


    def execute(self, queue, nick, msg, channel):
        words = msg.split()
        if len(words) < 2:
            print("nothing to similarize")
            return

        word = words[1]
        m = self.model.wv.most_similar (positive=word)
        results = []
        for result in m:
            val, prob = result
            results.append(val)

        ret_val = ' '.join(results)
        queue.put((ret_val, channel))