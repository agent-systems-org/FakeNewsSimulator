import datetime
import json
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import OneShotBehaviour, PeriodicBehaviour
from visualization import post_agent


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

        get_neighbours_behaviour = self.GetNeighboursBehaviour()
        self.add_behaviour(get_neighbours_behaviour)

        send_self_to_visualization = self.SendSelfToVisualization(
            period=10, start_at=datetime.datetime.now()
        )
        self.add_behaviour(send_self_to_visualization)

    class GetNeighboursBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(to=str(self.agent.graph_creator_jid))
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

    class SendSelfToVisualization(PeriodicBehaviour):
        async def run(self):
            post_agent(self.agent)
