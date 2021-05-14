import threading
import json
import requests
from .graph_v2 import HOST, PORT


URL = f"http://{HOST}:{PORT}"


def send_post(url, json_data):
    try:
        requests.post(url, json_data)
    except Exception:
        print(f"Couldn't post data to {url}")


def post_message(from_jid, to_jid, msg_type):
    """
    supported message types:
    "fakenews"
    "debunk"
    """
    data = json.dumps(
        {"from_jid": str(from_jid), "to_jid": str(to_jid), "type": msg_type}
    )
    threading.Thread(target=send_post, args=(URL + "/messages", data)).start()


def post_agents(agents):
    agents_data = []
    for agent in agents:
        agents_data.append(
            {
                "jid": str(agent.jid),
                "location": agent.location,
                "neighbours_count": len(agent.adj_list),
                "type": "dummy",
            }
        )

    data = json.dumps(agents_data)
    threading.Thread(target=send_post, args=(URL + "/agents", data)).start()
