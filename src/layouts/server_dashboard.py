from dash import html, dcc
from components.cpu import cpu_layout, update_historical_cpu_graph
from components.disk import disk_layout
from components.ram import ram_layout, update_historical_ram_graph
from components.logs import log_layout
from layouts.health import health_layout
from layouts.map import map_layout


def server_dashboard_layout(ip_list, current_ip):
    return html.Div(
        [
            html.H1(f"Server Dashboard: {current_ip}", className="text-center mb-20"),
            html.Div(
                [
                    html.Label("Switch Server:"),
                    dcc.Dropdown(
                        id="ip-switcher",
                        options=[{"label": ip, "value": ip} for ip in ip_list],
                        value=current_ip,
                        clearable=False,
                    ),
                ],
                className="card mb-20",
            ),
            # Refresh rate slider
            html.Div(
                [
                    html.Label("Refresh Rate (seconds):"),
                    dcc.Slider(
                        id="refresh-rate-slider",
                        min=5,
                        max=20,
                        step=None,
                        marks={5: "5s", 7: "7s", 10: "10s", 15: "15s", 20: "20s"},
                        value=5,
                    ),
                    html.Button(
                        "Set Refresh Rate",
                        id="set-refresh-rate",
                        n_clicks=0,
                        className="add-button",
                    ),
                ],
                className="card mb-20",
            ),
            # Main content grid
            html.Div(
                [
                    # Health and CPU info
                    html.Div(
                        [
                            health_layout(),
                            html.Div(id="cpu-core-info", className="mt-20"),
                        ],
                        className="card",
                    ),
                    # Log data
                    html.Div(id="log-data", className="card"),
                ],
                className="grid-container",
            ),
            # Realtime graphs section
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("CPU Usage", className="graph-title"),
                            dcc.Graph(id="cpu-graph", className="graph-content"),
                        ],
                        className="graph-container",
                    ),
                    html.Div(
                        [
                            html.H4("RAM Usage", className="graph-title"),
                            dcc.Graph(id="ram-graph", className="graph-content"),
                        ],
                        className="graph-container",
                    ),
                    html.Div(disk_layout(), className="graph-container"),
                ],
                className="graph-section",
            ),
            # Historical graphs section
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("Historical CPU Usage", className="graph-title"),
                            dcc.Graph(
                                id="historical-cpu-graph", className="graph-content"
                            ),
                        ],
                        className="graph-container",
                    ),
                    html.Div(
                        [
                            html.H4("Historical RAM Usage", className="graph-title"),
                            dcc.Graph(
                                id="historical-ram-graph", className="graph-content"
                            ),
                        ],
                        className="graph-container",
                    ),
                ],
                className="historical-graph-section",
            ),
            # Map and logs
            html.Div(
                [
                    html.Div(id="ip-map", className="map-container"),
                    html.Div(
                        id="recent-logs", className="recent-logs-container card mt-20"
                    ),
                ],
                className="map-logs-container",
            ),
            html.Div(id="ip-map-message", className="text-center mt-20"),
            # Hidden elements and intervals
            dcc.Interval(
                id="interval-component-server",
                interval=5 * 1000,
                n_intervals=0,
                disabled=True,
            ),
            html.Button("Add", id="add-button", style={"display": "none"}),
            dcc.Input(id="ip-input", style={"display": "none"}),
            html.Div(id="server-table-body", style={"display": "none"}),
            # Back button
            html.Div(
                [
                    html.Button(
                        "Back to Dashboard", id="back-button", className="add-button"
                    )
                ],
                className="text-center mt-20",
            ),
        ],
        className="dashboard-container",
    )
