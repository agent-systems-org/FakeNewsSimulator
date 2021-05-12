from spade.agent import Agent

from agents import DummyAgent #temporary
from spade.behaviour import CyclicBehaviour, State
from spade.message import Message
from spade.template import Template
import numpy as np
import random
import json

class GraphCreator(Agent):
    def __init__(self, jid, password, vertices_no, avg=None,
                 std=None, mapsize=100, verify_security=False):
        super().__init__(jid, password, verify_security)

        if avg is None:
            avg = vertices_no / 2.0

        if std is None:
            std = vertices_no / 2.0

        self.adj_list = {}
        self.locations = {}
        self.jid_map = {}
        self.agents = []
        self.jids = []
        self.avg = avg
        self.std = std
        self.vertices_no = vertices_no
        self.mapsize = mapsize
        self.domain_number = 0
        self.domain = jid.split('@')[1]
        [self.domain, self.domain_number] = self.domain.split('/')
        self.domain_number = int(self.domain_number)
        self.password = password

        print('Graph creator initialized')

    def generate_jids(self):
        for i in range(0, self.vertices_no):
            jid = f'test_agent@{self.domain}/{self.domain_number+i+1}'
            self.jids.append(jid)
            self.jid_map[jid] = i

    def generate_agents(self):
        for i in range(0, self.vertices_no):
            jid = self.jids[i]

            self.agents.append(DummyAgent(self.jid, jid, self.password, self.locations[i], self.adj_list[i]))


    def generate_adj_list(self):
        adj_n = [self.randn() for i in range(0, self.vertices_no)]
        for i in range(0, self.vertices_no):
            possible_vertices = self.jids.copy()
            possible_vertices.remove(self.jids[i])

            random.shuffle(possible_vertices)
            self.adj_list[i] = possible_vertices[:adj_n[i]]

    def generate_coordinates(self):
        self.locations = [
            (np.random.randint(0, self.mapsize), np.random.randint(0, self.mapsize))
            for i in range(0, self.vertices_no)
        ]


    def randn(self):
        x = np.random.normal(self.avg, self.std)
        x = max(1, x)
        x = min(self.vertices_no - 1, x)

        return int(x)

    async def setup(self):
        self.generate_coordinates()
        self.generate_jids()
        self.generate_adj_list()
        print('Initializing agents')
        self.generate_agents()

        template = Template()
        template.set_metadata('performative', 'query')
        b = self.InformAboutNeighboursBehaviour(self.adj_list, self.jid_map)
        self.add_behaviour(b, template)

    class InformAboutNeighboursBehaviour(CyclicBehaviour):
        def __init__ (self, adj_list, jid_map):
            super().__init__()
            self.adj_list = adj_list
            self.jid_map = jid_map
            print('Graph creator is ready to inform other agents about their neighbours')

        async def run(self):
            msg = await self.receive(timeout=10)
            
            if msg:
                sender_jid = str(msg.sender)

                if sender_jid not in self.jid_map:
                    return

                sender_id = self.jid_map[sender_jid]

                if sender_id not in self.adj_list:
                    return
                
                reply = msg.make_reply()
                reply.body = json.dumps({'neighbours' : self.adj_list[sender_id]})
                await self.send(reply)
