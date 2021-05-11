import datetime
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

    def log(self, msg):
        full_date = datetime.datetime.now()
        time = datetime.datetime.strftime(full_date, "%H:%M:%S")
        print(f"[{time}] {str(self.jid)}: {msg}")

    async def setup(self):
        self.log(
            f"dummy, location: {self.location}, neighbours: {self.adj_list}, created by: {self.graph_creator_jid}"
        )
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
                self.agent.log(
                    f"neighbours received from querying graph creator: {msg.body}"
                )
