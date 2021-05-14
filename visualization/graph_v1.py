"""
How to run:
in the main loop add the following code (after starting the agents):
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
"""

import networkx as nx
import matplotlib.pyplot as plt


def get_id(jid):
    return str(jid).split("/")[1]


def visualize_network(epoch, agents):
    print(f"Epoch: {epoch}")
    plt.clf()

    graph = nx.DiGraph()

    edges = []
    for agent in agents:
        # TODO get number of fakenews messages from an agent
        graph.add_node(
            get_id(agent.jid),
            attr_dict={
                "fakenews": 0,
                "state": "dummy",
                "neighbours": len(agent.adj_list),
            },
            pos=(agent.location),
        )

        # TODO display edges only when a message is sent
        for neighbour_jid in agent.adj_list:
            edges.append((get_id(agent.jid), get_id(neighbour_jid)))

    graph.add_edges_from(edges)

    # TODO add types to agents in the graph creator
    # so it's possible to draw them with different colors
    # we may also choose the color depending on how many fakenews messages
    # a node believes in
    # type_to_color_map = {"bot": 1.0, "common": 0.5, "influencer": 0.0}

    # TODO get type from the node (i.e. node.type)
    # node_colors = [type_to_color_map.get(node, 0.25) for node in G.nodes()]

    pos_dict = nx.get_node_attributes(graph, "pos")
    positions = {}
    for node, position in zip(pos_dict.keys(), pos_dict.values()):
        positions[node] = position

    # TODO use node_colors as node_color
    nx.draw_networkx_nodes(
        graph,
        positions,
        cmap=plt.get_cmap("jet"),
        node_color="r",
        node_size=500,
        alpha=0.5,
    )

    nx.draw_networkx_edges(graph, positions, arrows=True, arrowsize=15, alpha=0.5)

    attr_dict = nx.get_node_attributes(graph, "attr_dict")
    labels = {}
    for node, attr_dict in zip(graph.nodes(), attr_dict.values()):
        labels[node] = {
            "id": node,
            "f": attr_dict["fakenews"],
            "s": attr_dict["state"],
            "n": attr_dict["neighbours"],
        }

    nx.draw_networkx_labels(
        graph, positions, font_size=12, font_weight="bold", labels=labels
    )

    legend = """
    f - fakenews messages count
    s - state
    n - neighbours count
    """
    plt.text(0.02, 0.5, legend, fontsize=14, transform=plt.gcf().transFigure)
    plt.get_current_fig_manager().set_window_title("Fake news simulator")
    plt.title("Network graph")
