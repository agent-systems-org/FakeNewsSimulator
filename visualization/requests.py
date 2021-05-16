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


def post_messages(msgs):
    """
    non-blocking

    msgs is a list of messages

    a message: {
        "from_jid": JID
        "to_jid": JID
        "type": string
    }

    supported message types:
        "fakenews"
        "debunk"
    """

    msg_dicts = []
    for msg in msgs:
        msg_dicts.append(
            {
                "from_jid": str(msg["from_jid"]),
                "to_jid": str(msg["to_jid"]),
                "type": msg["type"],
            }
        )

    data = json.dumps(msg_dicts)
    threading.Thread(target=send_post, args=(URL + "/messages", data)).start()


def post_agent(agent):
    """
    non-blocking

    agent must have following properties:
        location: tuple (x, y)
        neighbours_count: number
        susceptibility: number [0; 100]
        susceptible_topic: string
        type: string

    supported agent types:
        "bot"
        "common"

    supported susceptible topics:
        "test"
    """

    agent_data = {
        str(agent.jid): {
            "location": agent.location,
            "neighbours_count": len(agent.adj_list),
            "susceptibility": agent.susceptibility,
            "susceptible_topic": agent.susceptible_topic,
            "type": agent.type,
        }
    }
    data = json.dumps(agent_data)
    threading.Thread(target=send_post, args=(URL + "/agents", data)).start()
