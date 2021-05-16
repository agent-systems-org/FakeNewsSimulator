import concurrent
import time
import sys
from spade import quit_spade
from agents import GraphCreator


AGENTS_DEFAULT_COUNT = 8


def main():
    if len(sys.argv) == 2:
        agents_count = int(sys.argv[1])
    else:
        agents_count = AGENTS_DEFAULT_COUNT

    print(f"Creating network with {agents_count} agents")

    first_jid = "test_agent@jabbim.pl/3000000"
    password = "123"

    graph_creator = GraphCreator(first_jid, password, agents_count)
    graph_creator.start().result()

    agents = graph_creator.agents

    # by default it uses at most 32 CPU cores
    with concurrent.futures.ThreadPoolExecutor() as e:
        e.submit([agent.start() for agent in agents])

    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            break

    for agent in agents + [graph_creator]:
        agent.stop()

    quit_spade()


if __name__ == "__main__":
    main()
