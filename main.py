import concurrent
import time
import sys
from spade import quit_spade
from agents import GraphCreator


AGENTS_DEFAULT_COUNT = 80


def main():
    if len(sys.argv) == 2:
        agents_count = int(sys.argv[1])
    else:
        agents_count = AGENTS_DEFAULT_COUNT

    print(f"Creating network with {agents_count} agents")

    # first_jid = "test_agent@jabbim.pl/1000"
    base = "fake_news"
    domain = "@jabbim.pl/1000"
    password = "12345"

    graph_creator = GraphCreator(base, domain, password, agents_count)
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


if __name__ == "__main__":
    main()
