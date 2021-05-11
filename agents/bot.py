import datetime
import random
import asyncio
from spade.behaviour import PeriodicBehaviour
from spade.agent import Agent
from spade.message import Message


MAX_INITIAL_DELAY_SEC = 1  # change to 30 after testing
MAX_PERIOD_SEC = 15  # change to 60 after testing


class Bot(Agent):
    def __init__(self, jid, password, location, adj_list, verify_security=False):
        super().__init__(jid, password, verify_security)
        self.location = location
        self.adj_list = adj_list
        self.delay = random.randint(1, MAX_INITIAL_DELAY_SEC)
        self.period = random.randint(1, MAX_PERIOD_SEC)
        self.fakenews_msgs = []

    def log(self, msg):
        full_date = datetime.datetime.now()
        time = datetime.datetime.strftime(full_date, "%H:%M:%S")
        print(f"[{time}] {str(self.jid)}: {msg}")

    async def setup(self):
        self.log(
            f"bot, delay: {self.delay}s, period: {self.period}s, location: {self.location}, neighbours: {self.adj_list}"
        )
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=self.delay)
        self.spread_fakenews_behaviour = self.SpreadFakenewsBehaviour(
            period=self.period, start_at=start_at
        )
        self.add_behaviour(self.spread_fakenews_behaviour)

    class SpreadFakenewsBehaviour(PeriodicBehaviour):
        async def run(self):
            if self.agent.adj_list and self.agent.fakenews_msgs:
                num_rand_recipients = random.randint(1, len(self.agent.adj_list))
                rand_recipients = random.choices(
                    self.agent.adj_list, k=num_rand_recipients
                )
                rand_fakenews_msg = random.choice(self.agent.fakenews_msgs)

                self.agent.log(
                    f"spreading {rand_fakenews_msg} to ({num_rand_recipients}) {rand_recipients}"
                )

                msgs = []
                for recipient in rand_recipients:
                    msg = Message()
                    msg.to = recipient
                    msgs.append(msg)

                await asyncio.wait([self.send(msg) for msg in msgs])

            else:
                self.agent.log(
                    f"couldn't spread fakenews, reason: neighbours: {self.agent.adj_list}, fakenews: {self.agent.fakenews_msgs}"
                )
