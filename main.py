import concurrent
import time
import sys
import getopt
import math
from spade import quit_spade
import matplotlib.pyplot as plt
from matplotlib import animation
import visualization
from agents import GraphCreator

DEFAULT_NUM_AGENTS = 80
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
    num_agents, IS_CONNECTIONS_VISUALIZATION_ON = parse_cli_args()

    base = "fake_news"
    # domain = "@jabbim.pl/5000"
    domain = "@localhost/1000"
    password = "12345"

    graph_creator = GraphCreator(base, domain, password, num_agents)
    print(f"Creating network with {num_agents} agents")

    graph_creator.start().result()

    agents = graph_creator.agents

    with concurrent.futures.ThreadPoolExecutor() as e:
        e.submit([agent.start() for agent in agents])

    if IS_CONNECTIONS_VISUALIZATION_ON:
        fig = plt.figure()

        _ = animation.FuncAnimation(
            fig,
            visualization.visualize_connections,
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

    for agent in agents:
        agent.stop()

    quit_spade()


if __name__ == "__main__":
    main()
