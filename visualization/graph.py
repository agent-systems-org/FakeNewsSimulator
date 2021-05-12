import networkx as nx
import matplotlib.pyplot as plt


def get_id(jid):
    return str(jid).split("/")[1]


def visualize_network(agents):
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

    pos = nx.spring_layout(G)

    # TODO use node_colors as node_color
    nx.draw_networkx_nodes(
        G, pos, cmap=plt.get_cmap("jet"), node_color="r", node_size=500, alpha=0.5,
    )
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=15, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=20)

    plt.show()
