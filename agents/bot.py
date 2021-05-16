import datetime
import random
import asyncio
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.agent import Agent
from spade.message import Message
from visualization import post_agent, post_messages


MAX_INITIAL_DELAY_SEC = 20
MAX_SPREAD_INTERVAL_SEC = 60
MAX_RECEIVE_TIME_SEC = 1000


class Bot(Agent):
    def __init__(self, jid, password, location, adj_list, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.location = location
        self.adj_list = adj_list
        self.delay = random.randint(1, MAX_INITIAL_DELAY_SEC)
        self.period = random.randint(1, MAX_SPREAD_INTERVAL_SEC)
        self.fakenews_msgs = []
        self.type = "bot"
        self.susceptibility = 100

    def log(self, msg):
        full_date = datetime.datetime.now()
        time = datetime.datetime.strftime(full_date, "%H:%M:%S")
        print(f"[{time}] {str(self.jid)}: {msg}")

    async def setup(self):
        self.log(
            f"bot, susceptibility: {self.susceptibility}, delay: {self.delay}s, period: {self.period}s, location: {self.location}, neighbours: {len(self.adj_list)}, fakenews: {len(self.fakenews_msgs)}"
        )

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=self.delay)
        self.spread_fakenews_behaviour = self.SpreadFakenewsBehaviour(
            period=self.period, start_at=start_at
        )
        self.add_behaviour(self.spread_fakenews_behaviour)

        self.receive_fakenews_behaviour = self.ReceiveFakenewsBehaviour()
        self.add_behaviour(self.receive_fakenews_behaviour)

        send_self_to_visualization = self.SendSelfToVisualization(
            period=10, start_at=datetime.datetime.now()
        )
        self.add_behaviour(send_self_to_visualization)

    class SpreadFakenewsBehaviour(PeriodicBehaviour):
        async def run(self):
            if self.agent.adj_list and self.agent.fakenews_msgs:
                num_rand_recipients = random.randint(1, len(self.agent.adj_list))
                rand_recipients = random.sample(
                    self.agent.adj_list, k=num_rand_recipients
                )
                rand_fakenews_msg = random.choice(self.agent.fakenews_msgs)

                self.agent.log(
                    f"spreading {rand_fakenews_msg} to ({num_rand_recipients}) {rand_recipients}"
                )

                msgs = []
                msgs_to_visualize = []
                for recipient in rand_recipients:
                    msg = Message()
                    msg.to = recipient
                    msg.body = rand_fakenews_msg
                    msgs.append(msg)
                    msgs_to_visualize.append(
                        {
                            "from_jid": self.agent.jid,
                            "to_jid": recipient,
                            "type": "fakenews",
                        }
                    )

                post_messages(msgs_to_visualize)
                await asyncio.wait([self.send(msg) for msg in msgs])

            else:
                self.agent.log(
                    f"couldn't spread fakenews, reason: neighbours: {self.agent.adj_list}, fakenews: {self.agent.fakenews_msgs}"
                )

    class ReceiveFakenewsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(MAX_RECEIVE_TIME_SEC)

            if not msg:
                self.agent.log("timeout or received message is empty")

            else:
                # TODO add checking if the recieved is fakenews
                if msg.body not in self.agent.fakenews_msgs:
                    self.agent.fakenews_msgs.append(msg.body)

                self.agent.log(
                    f"new message received: {msg.body}, fakenews messages: {self.agent.fakenews_msgs}"
                )

    class SendSelfToVisualization(PeriodicBehaviour):
        async def run(self):
            post_agent(self.agent)
