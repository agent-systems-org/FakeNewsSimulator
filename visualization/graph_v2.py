import json
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import networkx as nx


HOST = "127.0.0.1"
PORT = 8050
refresh_interval_ms = 10000
server_message_queue = []
server_agents = {}


def main():
    server = flask.Flask(__name__)

    @server.route("/messages", methods=["POST"])
    def post_messages():
        msgs = json.loads(flask.request.data)

        for msg in msgs:
            server_message_queue.append(msg)
            print(
                f"received msg: {msg}, current queue: {len(server_message_queue)} msgs"
            )

        return flask.Response("", 201)

    @server.route("/agents", methods=["POST"])
    def post_agents():
        agent_dict = json.loads(flask.request.data)
        agent_jid, agent_data = list(agent_dict.items())[0]

        try:
            server_agents[agent_jid] = agent_data
        except KeyError as e:
            print(f"Couldn't add agent {agent_dict}, reason: {e}")
            return flask.Response("", 418)

        print(f"received agent: {agent_dict}, total: {len(server_agents)} agents")
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
                    children=f"Refresh interval: {refresh_interval_ms / 1000}s",
                ),
                html.Div(children="Change the refresh interval:"),
                dcc.Slider(
                    id="refresh-interval-slider",
                    min=100,
                    max=60 * 1000,
                    step=100,
                    value=refresh_interval_ms,
                ),
                html.Div(id="state-text"),
                html.Button("stop", id="stop-button"),
                html.Button("resume", id="resume-button"),
                dcc.Graph(id="graph", style={"height": "100vh"}),
                dcc.Interval(
                    id="interval-component",
                    interval=refresh_interval_ms,
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
        global refresh_interval_ms
        context = dash.callback_context

        if (
            not context.triggered
            or context.triggered[0]["prop_id"].split(".")[0] == "resume-button"
        ):
            refresh_interval_text = f"Refresh interval: {refresh_interval_ms / 1000}s"
            state_text = "State: running"
            return [refresh_interval_ms, refresh_interval_text, state_text]

        elif context.triggered[0]["prop_id"].split(".")[0] == "stop-button":
            # it's impossible to stop the interval completely so I set it to a big value
            refresh_interval_text = f"Refresh interval: {refresh_interval_ms / 1000}s"
            state_text = "State: stopped"
            return [1000 * 60 * 60 * 24 * 365, refresh_interval_text, state_text]

        else:
            refresh_interval_ms = slider_value_ms
            refresh_interval_text = f"Refresh interval: {refresh_interval_ms / 1000}s"
            state_text = "State: running"
            return [refresh_interval_ms, refresh_interval_text, state_text]

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
        global server_message_queue

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
        for msg_data in server_message_queue:
            try:
                x0, y0 = server_agents[msg_data["from_jid"]]["location"]
                x1, y1 = server_agents[msg_data["to_jid"]]["location"]
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

        node_x = []
        node_y = []
        node_neighbours_count = []
        node_text = []
        markers = []
        for agent_data in server_agents.values():
            try:
                x, y = agent_data["location"]
                node_x.append(x)
                node_y.append(y)
                neighbours_count = agent_data["neighbours_count"]
                node_neighbours_count.append(neighbours_count)
                node_text.append(
                    f"neighbours: {neighbours_count}, fakenews messages: {agent_data['fakenews_count']}, type: {agent_data['type']}"
                )

                agent_type = agent_data["type"]
                if agent_type == "common":
                    markers.append("circle")
                elif agent_type == "bot":
                    markers.append("square")
                else:
                    markers.append("x-thin")
            except KeyError as e:
                print(f"Data on server is incomplete for {agent_data}, reason: {e}")

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            marker_symbol=markers,
            mode="markers",
            hoverinfo="text",
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale="YlGnBu",
                reversescale=True,
                color=node_neighbours_count,
                size=10,
                colorbar=dict(
                    thickness=15,
                    title="Node neighbours",
                    xanchor="left",
                    titleside="right",
                ),
                line_width=2,
            ),
        )

        fig.add_trace(node_trace)

        server_message_queue = []
        return fig

    app.run_server(debug=True, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
