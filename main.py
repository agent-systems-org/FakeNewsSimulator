import concurrent
import time
import sys
import getopt
import math
from spade import quit_spade
from agents import GraphCreator
import matplotlib.pyplot as plt
from matplotlib import animation
from visualization import visualize_connections


FIRST_JID = "test_agent@jabbim.pl/10000"
PASSWORD = "123"
DEFAULT_NUM_AGENTS = 16
DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON = False


def parse_cli_args():
    usage_str = f"Usage: {sys.argv[0]} [-h] [-n <num_of_agents> (default={DEFAULT_NUM_AGENTS})] [-v (toggle visualization of connections, default={DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON})]"

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hvn:")
    except getopt.GetoptError:
        print(usage_str)
        sys.exit(2)

    num_agents = DEFAULT_NUM_AGENTS
    is_connections_visualization_on = DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON

    for opt, arg in opts:
        if opt == "-h":
            print(usage_str)
            sys.exit(0)
        elif opt == "-n":
            num_agents = int(arg)
        elif opt == "-v":
            is_connections_visualization_on = (
                not DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON
            )

    return num_agents, is_connections_visualization_on


def main():
    NUM_AGENTS, IS_CONNECTIONS_VISUALIZATION_ON = parse_cli_args()

    print(f"Creating network with {NUM_AGENTS} agents")

    graph_creator = GraphCreator(FIRST_JID, PASSWORD, NUM_AGENTS)
    graph_creator.start().result()

    agents = graph_creator.agents

    with concurrent.futures.ThreadPoolExecutor() as e:
        e.submit([agent.start() for agent in agents])

    if IS_CONNECTIONS_VISUALIZATION_ON:
        fig = plt.figure()

        _ = animation.FuncAnimation(
            fig,
            visualize_connections,
            fargs=(agents,),
            interval=math.sqrt(len(agents)) * 1000,
        )

        plt.show()

    else:
        while True:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
