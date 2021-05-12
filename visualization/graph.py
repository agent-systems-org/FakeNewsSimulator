import networkx as nx
import matplotlib.pyplot as plt


def get_id(jid):
    return str(jid).split("/")[1]


def visualize_network(agents, pause_time_sec=5):
    G = nx.DiGraph()

    edges = []
    for agent in agents:
        # TODO get number of fakenews messages from an agent
        G.add_node(
            get_id(agent.jid),
            attr_dict={
                "fakenews": 0,
                "state": "dummy",
                "neighbours": len(agent.adj_list),
            },
            pos=(agent.location),
        )

        for neighbour_jid in agent.adj_list:
            edges.append((get_id(agent.jid), get_id(neighbour_jid)))

    G.add_edges_from(edges)

    # TODO add types to agents in the graph creator
    # so it's possible to draw them with different colors
    # we may also choose the color depending on how many fakenews messages
    # a node believes in
    # type_to_color_map = {"bot": 1.0, "common": 0.5, "influencer": 0.0}

    # TODO get type from the node (i.e. node.type)
    # node_colors = [type_to_color_map.get(node, 0.25) for node in G.nodes()]

    pos_dict = nx.get_node_attributes(G, "pos")
    positions = {}
    for node, position in zip(pos_dict.keys(), pos_dict.values()):
        positions[node] = position

    # TODO use node_colors as node_color
    nx.draw_networkx_nodes(
        G,
        positions,
        cmap=plt.get_cmap("jet"),
        node_color="r",
        node_size=500,
        alpha=0.5,
    )

    nx.draw_networkx_edges(G, positions, arrows=True, arrowsize=15, alpha=0.5)

    attr_dict = nx.get_node_attributes(G, "attr_dict")
    labels = {}
    for node, attr_dict in zip(G.nodes(), attr_dict.values()):
        labels[node] = {
            "id": node,
            "f": attr_dict["fakenews"],
            "s": attr_dict["state"],
            "n": attr_dict["neighbours"],
        }

    nx.draw_networkx_labels(
        G, positions, font_size=12, font_weight="bold", labels=labels
    )

    legend = """
    f - fakenews messages count
    s - state
    n - neighbours count
    """
    plt.text(0.02, 0.5, legend, fontsize=14, transform=plt.gcf().transFigure)
    plt.get_current_fig_manager().set_window_title("Fake news simulator")
    plt.title("Network graph")
    plt.show(block=False)
    plt.pause(pause_time_sec)
    plt.clf()
