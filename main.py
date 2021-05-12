import time
import concurrent
import sys
import math
from spade import quit_spade
from agents.graphcreator import GraphCreator
from visualization import visualize_network
import matplotlib.animation as animation
import matplotlib.pyplot as plt


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

    done, not_done = concurrent.futures.wait(
        [agent.start() for agent in agents],
        timeout=agents_count / 2,
        return_when=concurrent.futures.ALL_COMPLETED,
    )
    time.sleep(1)
    print(f"Created: {len(done)}, failed: {len(not_done)}")

    fig = plt.figure()
    # matplotlib requires to use this '_' variable. don't ask why. it's python.
    _ = animation.FuncAnimation(
        fig,
        visualize_network,
        fargs=(graph_creator.agents,),
        interval=math.sqrt(agents_count) * 1000,
    )
    plt.show()

    for agent in agents + [graph_creator]:
        agent.stop()

    quit_spade()


if __name__ == "__main__":
    main()
