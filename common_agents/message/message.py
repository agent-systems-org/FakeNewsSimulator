import random as rand
import itertools

class Message:
    newid = itertools.count().next
    def __init__(self, jid, topic):
        self.id = Message.newid() #each msg gets a unique incremented id
        self.creator_jid = jid
        self.emotion = {
                "attitude": rand.uniform(-1.0, 1.0),
                "arousal": rand.uniform(-1.0, 1.0)
                }
        self.persuation = rand.uniform(0,1)
        self.journalisic = rand.uniform(0,1)
        self.clickbait = double.uniform(0,1)
        self.topic = topic
        
