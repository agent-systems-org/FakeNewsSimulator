import random
import json
import numpy as np
from sklearn.neighbors import KDTree
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from .common import Common
from .bot import Bot
from .utils.message import NUM_TOPICS


class GraphCreator(Agent):
    def __init__(
        self,
        base,
        domain,
        password,
        vertices_no,
        avg=None,
        mapsize=100,
        verify_security=False,
    ):
        jid = base + "0" + domain
        super().__init__(jid, password, verify_security)

        if avg is None:
            avg = min(vertices_no ** 0.5, 700)

        self.adj_dict = {}
        self.locations = []
        self.location_tree = None
        self.jid_map = {}
        self.agents = []
        self.jids = []
        self.avg = avg
        self.vertices_no = vertices_no
        self.mapsize = mapsize
        # self.domain_number = 0
        # self.domain = jid.split("@")[1]
        [self.domain, self.domain_number] = domain.split("/")
        self.base_number = 0
        self.base = base
        self.domain_number = int(self.domain_number)
        self.password = password

        print("Graph creator initialized")

    def generate_jids(self):
        j = 0
        for i in range(self.vertices_no):
            jid = f"{self.base}{self.base_number}{self.domain}/{self.domain_number+j+1}"
            print(jid)
            self.jids.append(jid)
            self.jid_map[jid] = j
            j = j + 1
            if j == 10:
                self.base_number += 1
                j = 0

    def generate_agents(self):
        for i in range(self.vertices_no):
            topic = random.randint(0, NUM_TOPICS - 1)
            is_bot = random.random() < 0.1

            if is_bot:
                print("Creating a bot agent...")
                self.agents.append(
                    Bot(
                        self.jid,
                        self.jids[i],
                        self.password,
                        self.locations[i],
                        self.adj_dict[i],
                        topic,
                    )
                )
            else:
                print("Creating a common agent...")
                self.agents.append(
                    Common(
                        self.jid,
                        self.jids[i],
                        self.password,
                        self.locations[i],
                        self.adj_dict[i],
                        topic,
                    )
                )

    def generate_adj_dict(self):
        for i in range(self.vertices_no):
            self.adj_dict[i] = set()

        for i in range(self.vertices_no):
            num_neighbours = self.generate_num_of_neighbours()
            node_location = self.locations[i]

            # +1 becuase it also returns current location
            _, nearest_indices = self.location_tree.query(
                [node_location], k=num_neighbours + 1
            )
            neighbours_indices = nearest_indices[0][1:]
            neighbours = {self.jids[idx] for idx in neighbours_indices}

            p = 1 - num_neighbours / self.vertices_no
            bidirictional_connections_no = np.random.binomial(num_neighbours, p)

            for idx in neighbours_indices[:bidirictional_connections_no]:
                self.adj_dict[idx].add(self.jids[i])

            self.adj_dict[i] |= neighbours

    def generate_coordinates(self):
        dimensions = 2
        coordinates = np.random.random((self.vertices_no, dimensions)) * self.mapsize
        coordinates = list(map(tuple, coordinates))
        coordinates = [(round(x), round(y)) for x, y in coordinates]
        self.locations = coordinates
        self.location_tree = KDTree(coordinates)

    def generate_num_of_neighbours(self):
        x = np.random.exponential(self.avg)
        x = max(1, x)
        x = min(self.vertices_no - 1, x)
        return int(x)

    async def setup(self):
        self.generate_coordinates()
        self.generate_jids()
        self.generate_adj_dict()
        print("Initializing agents")
        self.generate_agents()

        template = Template()
        template.set_metadata("performative", "query")
        b = self.UpdateGraphBehaviour()
        self.add_behaviour(b, template)

    class UpdateGraphBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                sender_jid = str(msg.sender)
                body_json = json.loads(msg.body)
                user_to_follow_jid = str(body_json["follow"])

                if (
                    sender_jid not in self.agent.jid_map
                    or user_to_follow_jid not in self.agent.jid_map
                ):
                    return

                sender_id = self.agent.jid_map[sender_jid]
                user_to_follow_id = self.agent.jid_map[user_to_follow_jid]

                if (
                    sender_id not in self.agent.adj_dict
                    or user_to_follow_id not in self.agent.adj_dict
                ):
                    return

                self.agent.adj_dict[user_to_follow_id].add(sender_jid)
