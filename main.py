from agents.graphcreator import GraphCreator
from visualization import visualize_network
import time
import matplotlib.pyplot as plt


def main():
    jid = "test_agent@jabbim.pl/21360"

    g = GraphCreator(jid, "123", 8)

    future = g.start()
    future.result()

    agents = g.agents

    for agent in agents:
        future = agent.start()
        future.result()

    all_alive = lambda: all(
        map(lambda agent: agent.is_alive(), [agent for agent in agents])
    )

    while g.is_alive() and all_alive():
        try:
            visualize_network(g.agents, pause_time_sec=5)
            time.sleep(5)
        except KeyboardInterrupt:
            for agent in agents:
                agent.stop()

            g.stop()
            break


if __name__ == "__main__":
    main()
