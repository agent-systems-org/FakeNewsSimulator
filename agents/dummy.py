import datetime
import json
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import OneShotBehaviour
from visualization import post_message


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
        b = self.GetNeighboursBehaviour(self.graph_creator_jid)
        self.add_behaviour(b)

    class GetNeighboursBehaviour(OneShotBehaviour):
        def __init__(self, graph_creator_jid):
            super().__init__()
            self.graph_creator_jid = graph_creator_jid

        async def run(self):
            # TODO test message to be removed
            post_message(self.agent.jid, self.agent.graph_creator_jid, "query")

            msg = Message(to=str(self.graph_creator_jid))
            msg.set_metadata("performative", "query")
            await self.send(msg)

            msg = await self.receive(timeout=10)
            if msg:
                body_json = json.loads(msg.body)
                self.agent.log(
                    f"neighbours received from querying graph creator: {body_json['neighbours']}"
                )
            else:
                self.agent.log(
                    f"querying graph creator resulted in either timeout or empty message"
                )
