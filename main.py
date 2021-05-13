import concurrent
import sys
import math
from spade import quit_spade
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from agents import GraphCreator
from visualization import visualize_network


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

    with concurrent.futures.ThreadPoolExecutor() as e:
        e.submit([agent.start() for agent in agents])

    fig = plt.figure()
    # matplotlib requires to use this '_' variable. don't ask why. it's python.
    _ = animation.FuncAnimation(
        fig,
        visualize_network,
        fargs=(graph_creator.agents,),
        interval=math.sqrt(agents_count) * 1000,
    )

    # agents will start appearing while the GUI loop is running
    plt.show()

    for agent in agents + [graph_creator]:
        agent.stop()

    quit_spade()


if __name__ == "__main__":
    main()
