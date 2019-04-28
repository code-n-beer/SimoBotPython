import gensim 

class word2vecFeature:

    def __init__(self):
       self.cmdpairs = {
           "!similar": self.execute,
           "!similarn": self.executen,
           "!likexytoz": self.executexyz,
            "!xminusyplusz": self.execute_x_minus_y_plus_z
       }
       self.model = gensim.models.Word2Vec.load("./Resources/word2vec_2014-2019_04.model")

    def x_plus_y(self, x, y):
        return self.model.wv.similar_by_vector(
            self.model.wv.get_vector(x)
            + self.model.wv.get_vector(y))
    
    def x_minus_y(self, x, y):
        return self.model.wv.similar_by_vector(
            self.model.wv.get_vector(x)
            - self.model.wv.get_vector(y))
        
    def x_plus_y_minus_z(self, x, y, z):
        return self.x_minus_y(self.x_plus_y(x, y), z)

    def x_plus_y_plus_z(self, x, y, z):
        return self.x_plus_y(self.x_plus_y(x, y), z)

    def x_minus_y_plus_z(self, x, y, z):
        return self.x_plus_y(self.x_minus_y(x, y), z)

    def x_minus_y_minus_z(self, x, y, z):
        return self.x_minus_y(self.x_minus_y(x, y), z)
    

    def execute_x_minus_y_plus_z(self, queue, nick, msg, channel):
        words = msg.split()
        if len(words) < 4:
            print("nothing to similarize")
            return

        x = words[1]
        y = words[2]
        z = words[3]

        result = ""
        try:
            m = self.x_minus_y_plus_z(x,y,z)
            result = m
        except(KeyError):
            result = 'not found'

        ret_val = result.encode('utf-8').strip()
        queue.put((ret_val, channel))


    def executexyz(self, queue, nick, msg, channel):
        words = msg.split()
        if len(words) < 4:
            queue.put(('nothing to similarize', channel))
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
        if len(words) > 2:
            queue.put(('only one argument please, use similarn for many', channel))

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
