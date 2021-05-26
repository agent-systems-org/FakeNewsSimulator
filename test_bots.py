import time
import random
import concurrent
import math
import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from sklearn.neighbors import KDTree
from spade import quit_spade
from agents import Bot
from visualization import visualize_connections
from agents.utils import Message as News, NUM_TOPICS


ADDRESS = "test_agent@jabbim.pl/"
PASSWORD = "123"
FIRST_ID = 1000
MAX_COORD = 100
DIMENSIONS = 2
DEFAULT_NUM_BOTS = 32
DEFAULT_NUM_MSGS = 20
DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON = False


def parse_cli_args():
    usage_str = f"Usage: {sys.argv[0]} [-h] [-n <num_of_bots> (default={DEFAULT_NUM_BOTS})] [-m <num_of_msgs> (default={DEFAULT_NUM_MSGS})] [-v (run visualization of connections, default={DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON})]"

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hvn:m:")
    except getopt.GetoptError:
        print(usage_str)
        sys.exit(2)

    num_bots = DEFAULT_NUM_BOTS
    num_msgs = DEFAULT_NUM_MSGS
    is_connections_visualization_on = DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON

    for opt, arg in opts:
        if opt == "-h":
            print(usage_str)
            sys.exit(0)
        elif opt == "-n":
            num_bots = int(arg)
        elif opt == "-m":
            num_msgs = int(arg)
        elif opt == "-v":
            is_connections_visualization_on = (
                not DEFAULT_IS_CONNECTIONS_VISUALIZATION_ON
            )

    return num_bots, num_msgs, is_connections_visualization_on


if __name__ == "__main__":
    NUM_BOTS, NUM_MSGS, IS_CONNECTIONS_VISUALIZATION_ON = parse_cli_args()

    bots_addresses = [f"{ADDRESS}{FIRST_ID + i}" for i in range(NUM_BOTS)]
    msgs = [News(random.choice(bots_addresses)) for _ in range(NUM_MSGS)]
    for msg in msgs:
        msg.new(random.randint(0, NUM_TOPICS - 1))

    # generate uniformly distributed coordinates
    X = np.random.random((NUM_BOTS, DIMENSIONS)) * MAX_COORD

    # change type to list of tuples
    coordinates = list(map(tuple, X))
    coordinates = [(round(x), round(y)) for x, y in coordinates]
    kd_tree = KDTree(coordinates)

    bots = []
    for i in range(NUM_BOTS):
        location = coordinates[i]

        # uniformly distributed
        # a bot cannot be a neighbour with itself
        num_neigbours = random.randint(0, NUM_BOTS - 1)

        # +1 becuase it also returns current location
        _, nearest_indices = kd_tree.query([location], k=num_neigbours + 1)
        neighbours_indices = nearest_indices[0][1:]
        neighbours = [bots_addresses[idx] for idx in neighbours_indices]

        topic = random.randint(0, NUM_TOPICS - 1)
        bot = Bot(bots_addresses[i], PASSWORD, location, neighbours, topic)

        num_fakenews_msgs = random.randint(0, NUM_MSGS)
        fakenews_msgs = random.sample(msgs, num_fakenews_msgs)
        bot.fakenews_msgs = fakenews_msgs

        bots.append(bot)

    with concurrent.futures.ThreadPoolExecutor() as e:
        e.submit([bot.start() for bot in bots])

    if IS_CONNECTIONS_VISUALIZATION_ON:
        fig = plt.figure()

        _ = animation.FuncAnimation(
            fig,
            visualize_connections,
            fargs=(bots,),
            interval=math.sqrt(len(bots)) * 1000,
        )

        plt.show()

    else:
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

    for bot in bots:
        bot.stop()

    quit_spade()
