from agents.graphcreator import GraphCreator
from spade import quit_spade
from visualization import visualize_network
import time
import concurrent
import sys


AGENTS_DEFAULT_COUNT = 16


def main():
    if len(sys.argv) == 2:
        agents_count = int(sys.argv[1])
    else:
        agents_count = AGENTS_DEFAULT_COUNT

    print(f"Creating network with {agents_count} agents")

    jid = "test_agent@jabbim.pl/2000000"

    g = GraphCreator(jid, "123", agents_count)

    future = g.start()
    future.result()

    agents = g.agents

    done, not_done = concurrent.futures.wait(
        [agent.start() for agent in agents],
        timeout=agents_count / 2,
        return_when=concurrent.futures.ALL_COMPLETED,
    )
    time.sleep(1)
    print(f"created: {len(done)}, failed: {len(not_done)}")

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

    quit_spade()


if __name__ == "__main__":
    main()
