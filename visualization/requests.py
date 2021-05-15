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


def create_msg_dict(msg):
    return {
        "from_jid": str(msg["from_jid"]),
        "to_jid": str(msg["to_jid"]),
        "type": msg["type"],
    }


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
        msg_dicts.append(create_msg_dict(msg))

    data = json.dumps(msg_dicts)
    threading.Thread(target=send_post, args=(URL + "/messages", data)).start()


def create_agent_dict(agent):
    return {
        "location": agent.location,
        "neighbours_count": len(agent.adj_list),
        "fakenews_count": len(agent.fakenews_msgs),
        "type": agent.type,
    }


def post_agent(agent):
    """
    non-blocking

    agent must have following properties:
        location: tuple (x, y)
        neighbours_count: number
        fakenews_count: number
        type: string

    supported agent types:
        "bot"
        "common"
    """
    agent_data = {str(agent.jid): create_agent_dict(agent)}
    data = json.dumps(agent_data)
    threading.Thread(target=send_post, args=(URL + "/agents", data)).start()
