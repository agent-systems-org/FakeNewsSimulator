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
        jid,
        password,
        vertices_no,
        avg=None,
        std=None,
        mapsize=100,
        verify_security=False,
    ):
        super().__init__(jid, password, verify_security)

        if avg is None:
            avg = vertices_no / 2.0

        if std is None:
            std = vertices_no / 2.0

        self.adj_dict = {}
        self.locations = []
        self.location_tree = None
        self.jid_map = {}
        self.agents = []
        self.jids = []
        self.avg = avg
        self.std = std
        self.vertices_no = vertices_no
        self.mapsize = mapsize
        self.domain_number = 0
        self.domain = jid.split("@")[1]
        [self.domain, self.domain_number] = self.domain.split("/")
        self.domain_number = int(self.domain_number)
        self.password = password

        print("Graph creator initialized")

    def generate_jids(self):
        for i in range(self.vertices_no):
            jid = f"test_agent@{self.domain}/{self.domain_number+i+1}"
            self.jids.append(jid)
            self.jid_map[jid] = i

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
            num_neighbours = self.generate_num_of_neighbours()
            node_location = self.locations[i]

            # +1 becuase it also returns current location
            _, nearest_indices = self.location_tree.query(
                [node_location], k=num_neighbours + 1
            )
            neighbours_indices = nearest_indices[0][1:]
            neighbours = [self.jids[idx] for idx in neighbours_indices]

            self.adj_dict[i] = neighbours

    def generate_coordinates(self):
        dimensions = 2
        coordinates = np.random.random((self.vertices_no, dimensions)) * self.mapsize
        coordinates = list(map(tuple, coordinates))
        coordinates = [(round(x), round(y)) for x, y in coordinates]
        self.locations = coordinates
        self.location_tree = KDTree(coordinates)

    def generate_num_of_neighbours(self):
        x = np.random.normal(self.avg, self.std)
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
        b = self.InformAboutNeighboursBehaviour(self.adj_dict, self.jid_map)
        self.add_behaviour(b, template)

    class InformAboutNeighboursBehaviour(CyclicBehaviour):
        def __init__(self, adj_dict, jid_map):
            super().__init__()
            self.adj_dict = adj_dict
            self.jid_map = jid_map
            print(
                "Graph creator is ready to inform other agents about their neighbours"
            )

        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                sender_jid = str(msg.sender)

                if sender_jid not in self.jid_map:
                    return

                sender_id = self.jid_map[sender_jid]

                if sender_id not in self.adj_dict:
                    return

                reply = msg.make_reply()
                reply.body = json.dumps({"neighbours": self.adj_dict[sender_id]})
                await self.send(reply)
