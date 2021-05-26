import random
import datetime
import asyncio
from agents.utils import Message as News
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.agent import Agent
from spade.message import Message
from visualization import post_agent, post_messages

INIT_SUSCEPTIBILITY = 50  # TBD
MAX_RECEIVE_TIME_SEC = 1000
MAX_INITIAL_DELAY_SEC = 30
MAX_SPREAD_INTERVAL_SEC = 120
CONVERGENCE = 16
SEND_SELF_PERIOD_SEC = 10


class Common(Agent):
    def __init__(
        self, graph_creator_jid, jid, pswd, loc, adj, topic=0, verify_security=False
    ):
        super().__init__(jid, pswd, verify_security)
        self.location = loc
        self.adj_list = adj
        self.beliving = []
        self.debunking = []
        self.graph_creator_jid = graph_creator_jid
        self.susceptibility = INIT_SUSCEPTIBILITY
        self.susceptible_topic = topic
        self.period_debunk = random.randint(3, MAX_SPREAD_INTERVAL_SEC)
        self.period_share = random.randint(3, MAX_SPREAD_INTERVAL_SEC)
        self.delay = random.randint(1, MAX_INITIAL_DELAY_SEC)
        self.type = "common"

    def log(self, msg):
        full_date = datetime.datetime.now()
        time = datetime.datetime.strftime(full_date, "%H:%M:%S")
        print(f"[{time}] {str(self.jid)}: {msg}")

    async def setup(self):
        self.log(
            f"common, location: {self.location}, neighbours: {self.adj_list}, susceptible topic: {self.susceptible_topic}"
        )

        self.accept_news_behaviour = self.AcceptNews()
        self.add_behaviour(self.accept_news_behaviour)

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=self.delay)
        self.share_news_behaviour = self.ShareNews(
            period=self.period_share, start_at=start_at
        )
        self.add_behaviour(self.share_news_behaviour)

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=self.delay)
        self.debunk_behaviour = self.ShareDebunk(
            period=self.period_debunk, start_at=start_at
        )
        self.add_behaviour(self.debunk_behaviour)

        self.send_self_to_visualization = self.SendSelfToVisualization(
            period=SEND_SELF_PERIOD_SEC, start_at=datetime.datetime.now()
        )
        self.add_behaviour(self.send_self_to_visualization)

    class AcceptNews(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(MAX_RECEIVE_TIME_SEC)

            if not msg:
                self.agent.log("timeout or received msg is empty")
            else:
                # read msg
                content = News.fromJSON(msg.body)
                # check if msg was previously received
                # if content.id in self.agent.beliving:
                #     # TODO share msg + evolution (?)
                #     self.agent.log(f"already received msg {content.id}")
                # elif content.id in self.agent.debunking:
                #     # TODO share debunk yee haw
                #     self.agent.log(f"already received msg {content.id}")
                if (content not in self.agent.beliving) and (
                    content not in self.agent.debunking
                ):
                    # its math time
                    msg_power = content.calculate_power()
                    expected_score = 1 / (
                        1 + 10 ** ((msg_power - self.agent.susceptibility) / 50)
                    )
                    result = random.uniform(0, 100)
                    if result > 50 - (
                        msg_power - self.agent.susceptibility
                    ):  # accept the msg
                        self.agent.susceptibility = (
                            self.agent.susceptibility
                            + CONVERGENCE * (1 - expected_score)
                        )
                        self.agent.beliving.append(content)
                    else:  # refute the msg
                        self.agent.susceptibility = (
                            self.agent.susceptibility + CONVERGENCE * (-expected_score)
                        )
                        self.agent.debunking.append(content)

    class ShareNews(PeriodicBehaviour):
        async def run(self):
            if self.agent.adj_list and self.agent.beliving:
                num_rand_recipients = random.randint(1, len(self.agent.adj_list))
                rand_recipients = random.sample(
                    self.agent.adj_list, k=num_rand_recipients
                )
                rand_fakenews_msg = random.choice(self.agent.beliving)
                self.agent.log(
                    f"spreading fake news to {num_rand_recipients} recipients"
                )
                msgs = []
                for recipient in rand_recipients:
                    msg = Message()
                    msg.to = recipient
                    msg.body = rand_fakenews_msg.toJSON()
                    msgs.append(msg)

                await asyncio.wait([self.send(msg) for msg in msgs])
            else:
                self.agent.log(
                    f"couldn't spread news, reason: neighbours: {self.agent.adj_list}, fakenews: {self.agent.beliving}"
                )

    class ShareDebunk(PeriodicBehaviour):
        async def run(self):
            if self.agent.adj_list and self.agent.debunking:
                num_rand_recipients = random.randint(1, len(self.agent.adj_list))
                rand_recipients = random.sample(
                    self.agent.adj_list, k=num_rand_recipients
                )
                to_debunk = random.choice(self.agent.debunking)

                debunk_msg = News(self.agent.jid)
                debunk_msg.new_debunk(to_debunk.id, to_debunk.topic)
                self.agent.log(f"spreading debunk to {num_rand_recipients} recipients")
                msgs = []
                for recipient in rand_recipients:
                    msg = Message()
                    msg.to = recipient
                    msg.body = debunk_msg.toJSON()
                    msgs.append(msg)

                await asyncio.wait([self.send(msg) for msg in msgs])
            else:
                self.agent.log(
                    f"couldn't spread debunk, reason: neighbours: {self.agent.adj_list}, fakenews: {self.agent.fakenews_msgs}"
                )

    class SendSelfToVisualization(PeriodicBehaviour):
        async def run(self):
            post_agent(self.agent)
