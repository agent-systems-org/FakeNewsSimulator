import sys
import os
import threading
import webbrowser
import json
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


HOST = "127.0.0.1"
PORT = 8050
REFRESH_INTERVAL_MS = 10000
SERVER_MESSAGE_QUEUE = []
SERVER_AGENTS = {}


def main():
    server = flask.Flask(__name__)

    @server.route("/messages", methods=["POST"])
    def post_messages():
        msgs = json.loads(flask.request.data)

        for msg in msgs:
            SERVER_MESSAGE_QUEUE.append(msg)
            print(
                f"received msg: {msg}, current queue: {len(SERVER_MESSAGE_QUEUE)} msgs"
            )

        return flask.Response("", 201)

    @server.route("/agents", methods=["POST"])
    def post_agents():
        agent_dict = json.loads(flask.request.data)
        agent_jid, agent_data = list(agent_dict.items())[0]

        try:
            SERVER_AGENTS[agent_jid] = agent_data
        except KeyError as e:
            print(f"Couldn't add agent {agent_dict}, reason: {e}")
            return flask.Response("", 418)

        print(f"received agent: {agent_dict}, total: {len(SERVER_AGENTS)} agents")
        return flask.Response("", 201)

    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
    app.layout = html.Div(
        html.Div(
            [
                html.H4("Fakenews simulator - network graph"),
                html.Div(id="epoch-text"),
                html.Div(
                    id="refresh-interval-text",
                    children=f"Refresh interval: {REFRESH_INTERVAL_MS / 1000}s",
                ),
                html.Div(children="Change the refresh interval:"),
                dcc.Slider(
                    id="refresh-interval-slider",
                    min=100,
                    max=60 * 1000,
                    step=100,
                    value=REFRESH_INTERVAL_MS,
                ),
                html.Div(id="state-text"),
                html.Button("stop", id="stop-button"),
                html.Button("resume", id="resume-button"),
                dcc.Graph(id="graph", style={"height": "100vh"}),
                dcc.Interval(
                    id="interval-component",
                    interval=REFRESH_INTERVAL_MS,
                    n_intervals=0,
                ),
            ]
        )
    )

    # note to self: if you ever see a python library that says "no js required" just don't use it
    @app.callback(
        [
            Output("interval-component", "interval"),
            Output("refresh-interval-text", "children"),
            Output("state-text", "children"),
        ],
        [
            Input("stop-button", "n_clicks"),
            Input("resume-button", "n_clicks"),
            Input("refresh-interval-slider", "value"),
        ],
    )
    def modify_interval(stop, resume, slider_value_ms):
        global REFRESH_INTERVAL_MS
        context = dash.callback_context

        if (
            not context.triggered
            or context.triggered[0]["prop_id"].split(".")[0] == "resume-button"
        ):
            refresh_interval_text = f"Refresh interval: {REFRESH_INTERVAL_MS / 1000}s"
            state_text = "State: running"
            return [REFRESH_INTERVAL_MS, refresh_interval_text, state_text]

        elif context.triggered[0]["prop_id"].split(".")[0] == "stop-button":
            # it's impossible to stop the interval completely so I set it to a big value
            refresh_interval_text = f"Refresh interval: {REFRESH_INTERVAL_MS / 1000}s"
            state_text = "State: stopped"
            return [1000 * 60 * 60 * 24 * 365, refresh_interval_text, state_text]

        else:
            REFRESH_INTERVAL_MS = slider_value_ms
            refresh_interval_text = f"Refresh interval: {REFRESH_INTERVAL_MS / 1000}s"
            state_text = "State: running"
            return [REFRESH_INTERVAL_MS, refresh_interval_text, state_text]

    @app.callback(
        Output("epoch-text", "children"),
        Input("interval-component", "n_intervals"),
    )
    def update_epoch(n_intervals):
        return html.Span(f"Epoch: {n_intervals}")

    @app.callback(
        Output("graph", "figure"),
        Input("interval-component", "n_intervals"),
    )
    def update_graph(n_intervals):
        # it's cleared after reading all pending messages
        global SERVER_MESSAGE_QUEUE

        fig = go.Figure(
            layout=go.Layout(
                titlefont_size=16,
                showlegend=False,
                hovermode="closest",
                annotations=[
                    dict(
                        text="<a href='https://github.com/agent-systems-org/FakeNewsSimulator/'>Source</a>",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.005,
                        y=-0.002,
                    )
                ],
                margin=dict(b=20, l=5, r=5, t=20),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        edges = {
            "fakenews": {
                "edge_x": [],
                "edge_y": [],
                "style": dict(width=0.5, color="rgb(255,0,0)"),
            },
            "debunk": {
                "edge_x": [],
                "edge_y": [],
                "style": dict(width=0.5, color="rgb(0,255,0)"),
            },
        }
        for msg_data in SERVER_MESSAGE_QUEUE:
            try:
                x0, y0 = SERVER_AGENTS[msg_data["from_jid"]]["location"]
                x1, y1 = SERVER_AGENTS[msg_data["to_jid"]]["location"]
                msg_type = msg_data["type"]
                edges[msg_type]["edge_x"].append(x0)
                edges[msg_type]["edge_x"].append(x1)
                edges[msg_type]["edge_x"].append(None)
                edges[msg_type]["edge_y"].append(y0)
                edges[msg_type]["edge_y"].append(y1)
                edges[msg_type]["edge_y"].append(None)

            except KeyError as e:
                print(f"Data on server is incomplete for {msg_data}, reason: {e}")

        for edge_type_dict in edges.values():
            edge_trace = go.Scatter(
                x=edge_type_dict["edge_x"],
                y=edge_type_dict["edge_y"],
                line=edge_type_dict["style"],
                hoverinfo="none",
                mode="lines",
            )
            fig.add_trace(edge_trace)

        # prevents race conditions
        agents_data_copy = list(SERVER_AGENTS.values())

        max_neighbours = -sys.maxsize
        min_neighbours = sys.maxsize
        for agent_data in agents_data_copy:
            try:
                if agent_data["neighbours_count"] < min_neighbours:
                    min_neighbours = agent_data["neighbours_count"]

                elif agent_data["neighbours_count"] > max_neighbours:
                    max_neighbours = agent_data["neighbours_count"]

            except KeyError as e:
                print(f"Data on server is incomplete for {agent_data}, reason: {e}")

        if max_neighbours != min_neighbours:
            marker_max_size = 18
            marker_min_size = 3
            a_marker_coeff = (marker_max_size - marker_min_size) / (
                max_neighbours - min_neighbours
            )
            b_marker_coeff = marker_max_size - max_neighbours * a_marker_coeff
            get_marker_size = lambda n_count: n_count * a_marker_coeff + b_marker_coeff
        else:
            get_marker_size = lambda n_count: 10

        max_susceptibility = 100
        min_susceptibility = 0
        max_saturation = 100
        min_saturation = 25
        a_sus_coeff = (max_saturation - min_saturation) / (
            max_susceptibility - min_susceptibility
        )
        b_sus_coeff = max_saturation - max_susceptibility * a_sus_coeff
        get_saturation = lambda sus: sus * a_sus_coeff + b_sus_coeff

        for agent_data in agents_data_copy:
            try:
                x, y = agent_data["location"]

                agent_type = agent_data["type"]
                if agent_type == "common":
                    marker_symbol = "circle"
                elif agent_type == "bot":
                    marker_symbol = "square"
                else:
                    marker_symbol = "x-thin"

                # TODO add more colors (hue values) for different topics
                susceptible_topic = agent_data["susceptible_topic"]
                susceptibility = agent_data["susceptibility"]
                if susceptible_topic == "test":
                    hue = 150

                color = f"hsv({hue},{get_saturation(susceptibility)}%,100%)"

                neighbours_count = agent_data["neighbours_count"]

                node_trace = go.Scatter(
                    x=[x],
                    y=[y],
                    marker_symbol=marker_symbol,
                    marker=dict(size=get_marker_size(neighbours_count), color=color),
                    mode="markers",
                    hoverinfo="text",
                    text=f"neighbours: {neighbours_count}, susceptible topic: {susceptible_topic}, susceptibility: {susceptibility}, type: {agent_data['type']}",
                )
                fig.add_trace(node_trace)

            except KeyError as e:
                print(f"Data on server is incomplete for {agent_data}, reason: {e}")

        SERVER_MESSAGE_QUEUE = []
        return fig

    app.run_server(debug=True, host=HOST, port=PORT)


def open_new_tab():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new_tab(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    threading.Timer(1, open_new_tab).start()
    main()
