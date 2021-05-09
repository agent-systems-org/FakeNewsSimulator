from spade.agent import Agent

class DummyAgent(Agent):
    def __init__(self, jid, password, location, adj_list, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.location = location
        self.adj_list = adj_list

    async def setup(self):
        print("Hello World! I'm agent {} my location is {}".format(str(self.jid), str(self.location)))
        print("My neighbours {}".format(self.adj_list))
