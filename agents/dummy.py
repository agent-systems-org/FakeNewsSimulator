from spade.agent import Agent
from spade.message import Message
from spade.behaviour import OneShotBehaviour


class DummyAgent(Agent):
    def __init__(
        self,
        graph_creator_jid,
        jid,
        password,
        location,
        adj_list,
        verify_security=False,
    ):
        super().__init__(jid, password, verify_security)
        self.location = location
        self.adj_list = adj_list
        self.graph_creator_jid = graph_creator_jid

    async def setup(self):
        print(
            "Hello World! I'm agent {} my location is {}".format(
                str(self.jid), str(self.location)
            )
        )
        print("My neighbours {}".format(self.adj_list))
        print("I was created by {}".format(self.graph_creator_jid))
        b = self.getNeighbours(self.graph_creator_jid)
        self.add_behaviour(b)

    class getNeighbours(OneShotBehaviour):
        def __init__(self, graph_creator_jid):
            super().__init__()
            self.graph_creator_jid = graph_creator_jid

        async def run(self):
            msg = Message(to=str(self.graph_creator_jid))
            msg.set_metadata("performative", "query")
            await self.send(msg)

            msg = await self.receive(timeout=10)
            if msg:
                print(msg.body)
