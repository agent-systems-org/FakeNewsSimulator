from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.agent import Agent
from spade.message import Message

class Common(Agent):
    def __init__(self, jid, pswd, loc, adj, topic = 0, verify_security=False):
       super().__init__(jid, pswd, verify_security)
       self.location = loc
       self.adj_list = adj
       self.beliving = []
       self.debunking = []
       self.disposition = 0.5 ##TBD
       self.topic = topic

    def log(self, msg):
        full_date = datetime.datetime.now
        time = datetime.datetime.strftime(full_date, "%H:%M:%S")
        print(f"[{time}] {str(self.jid)}: {msg}")

    async def setup(self):
        self.log(
            f"common, location: {self.location}, neighbours: {self.adj_list}, topic: {self.topic}")

