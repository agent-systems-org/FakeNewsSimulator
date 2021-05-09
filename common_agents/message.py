import random as rand
import itertools
import json
from types import SimpleNamespace

class Message:
    id_iter = itertools.count()
    def __init__(self, jid):
        """ Creates a message instance


            Before using the message further methods need be called
            jid -- creator's jid
        """
        self.creator_jid = jid

    def new(self, topic):
        """ Generates new random message  

            topic -- message's topic
        """
        self.id = next(Message.id_iter) #each msg gets a unique incremented id
        self.emotion = {
                "attitude": rand.uniform(-1.0, 1.0),
                "arousal": rand.uniform(-1.0, 1.0)
                }
        self.persuation = rand.uniform(0,1)
        self.journalistic = rand.uniform(0,1)
        self.clickbait = rand.uniform(0,1)
        self.topic = topic
        self.debunking = False
        self.debunk_id = -1
    def new_debunk(self, debunk_id, debunk_topic):
        """ Generates new debunking message for a given fake news 

            debunk_id -- id of the message we are debunking
            debunk_topic -- topic of the message we are debunking
        """

        self.id = next(Message.id_iter) #each msg gets a unique incremented id
        self.emotion = {
                "attitude": rand.uniform(-1.0, 1.0),
                "arousal": rand.uniform(-1.0, 1.0)
                }
        self.persuation = rand.uniform(0,1)
        self.journalistic = rand.uniform(0,1)
        self.clickbait = rand.uniform(0,1)
        self.topic = debunk_topic
        self.debunking = True
        if(debunk_id < 0):
            raise ValueError("Id of the message must be a positive integer!")
        self.debunk_id = debunk_id

    def fromJSON(self, msg_json):
        """ Loads message data from a JSON string

            msg_json - json represenation of a message
        """
        tmp = json.loads(msg_json, object_hook=lambda d: SimpleNamespace(**d))
        self.id = tmp.id
        self.topic = tmp.topic
        self.creator_jid = tmp.creator_jid
        self.emotion = {}
        self.emotion["attitude"] = tmp.emotion.attitude
        self.emotion["arousal"] = tmp.emotion.arousal
        self.persuation = tmp.persuation
        self.journalistic = tmp.journalistic
        self.clickbait = tmp.clickbait
        self.debunking = tmp.debunking
        self.debunk_id = tmp.debunk_id
    
    def toJSON(self):
        """ Converts a Message into a JSON and returns as string """
        return json.dumps(self.__dict__)

        
     
