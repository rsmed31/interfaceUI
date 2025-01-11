from dash import html, dcc
from components.logs import aggregated_log_layout
import urllib.parse


def main_dashboard_layout(ip_list):
    table_rows = create_table_rows(ip_list, {})
    if not table_rows:
        table_rows = [
            html.Tr(
                [
                    html.Td(
                        "Please add a server to monitor",
                        colSpan=8,
                        style={"textAlign": "center"},
                    )
                ]
            )
        ]

    return html.Div(
        [
            html.H1("Server Monitoring Dashboard", className="text-center mb-20"),
            # Input container
            html.Div(
                [
                    dcc.Input(
                        id="ip-input",
                        type="text",
                        placeholder="Enter IP Address",
                        className="ip-input",
                    ),
                    html.Button(
                        "Add", id="add-button", n_clicks=0, className="add-button"
                    ),
                ],
                className="text-center mb-20",
            ),
            # Server table in card container
            html.Div(
                [
                    html.Table(
                        [
                            html.Thead(
                                [
                                    html.Tr(
                                        [
                                            html.Th("IP Address"),
                                            html.Th("Health"),
                                            html.Th("Processor Name"),
                                            html.Th("Number of Cores"),
                                            html.Th("Frequency (MHz)"),
                                            html.Th("Connected Users"),
                                            html.Th("Actions"),
                                            html.Th("Delete"),
                                        ]
                                    )
                                ]
                            ),
                            html.Tbody(id="server-table-body", children=table_rows),
                        ],
                        className="styled-table",
                    )
                ],
                className="card",
            ),
            # Stats cards
            html.Div(
                [
                    # Aggregated log data
                    html.Div(id="aggregated-log-data", className="card"),
                    # Average usage
                    html.Div(
                        [
                            html.H3("Average Usage", className="text-center mb-20"),
                            html.Div(id="average-usage", className="average-usage"),
                        ],
                        className="card",
                    ),
                ],
                className="grid-container",
            ),
            # Hidden elements
            dcc.Dropdown(id="ip-switcher", style={"display": "none"}),
            html.Button(id="back-button", style={"display": "none"}),
            dcc.Graph(id="cpu-graph", style={"display": "none"}),
            dcc.Graph(id="ram-graph", style={"display": "none"}),
            dcc.Interval(
                id="interval-component-server",
                interval=5 * 1000,
                n_intervals=0,
                disabled=True,
            ),
        ],
        className="dashboard-container",
    )


def create_table_rows(ip_list, ip_data):
    rows = []
    for ip in ip_list:
        if ip not in ip_data:
            ip_data[ip] = {
                "health": "Fetching...",
                "processor_name": "Fetching...",
                "number_of_cores": "Fetching...",
                "frequency": "Fetching...",
                "connected_users": "Fetching...",
            }

        data = ip_data[ip]
        # Ensure IP is properly encoded for both the link and button ID
        encoded_ip = urllib.parse.quote(ip)
        rows.append(
            html.Tr(
                [
                    html.Td(
                        dcc.Link(
                            ip,  # Show original IP
                            href=f"/server/{encoded_ip}",
                            style={
                                "color": "blue",
                                "textDecoration": "underline",
                                "cursor": "pointer",
                            },
                        )
                    ),
                    html.Td(data["health"]),
                    html.Td(data["processor_name"]),
                    html.Td(data["number_of_cores"]),
                    html.Td(data["frequency"]),
                    html.Td(data["connected_users"]),
                    html.Td(
                        html.Button(
                            "Retry",
                            id={"type": "retry-button", "ip": encoded_ip},
                            n_clicks=0,
                            className="add-button",
                        )
                    ),
                    html.Td(
                        html.Button(
                            "Delete",
                            id={"type": "delete-button", "ip": encoded_ip},
                            n_clicks=0,
                            className="add-button",
                        )
                    ),
                ]
            )
        )
    return rows
