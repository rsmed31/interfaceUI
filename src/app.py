import asyncio
import urllib.parse
import json
import ast
import os
import time
from dash import Dash, dcc, html, no_update, callback_context
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from components.cpu import update_cpu_graph, update_historical_cpu_graph
from components.ram import update_ram_graph, update_historical_ram_graph
from components.disk import update_disk_graph
from components.logs import log_layout, aggregated_log_layout, recent_logs_layout
from services.api_service import fetch_data, set_base_url, fetch_all_data
from layouts.main_dashboard import main_dashboard_layout, create_table_rows
from layouts.server_dashboard import server_dashboard_layout
from layouts.health import health_layout
from datetime import datetime
import plotly.graph_objects as go
from layouts.map import map_layout
from services.api_service import fetch_geolocation

# Define the path to the JSON file
DATA_FILE = "ip_data.json"


# Function to load IP data from the JSON file
def load_ip_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


# Function to save IP data to the JSON file
def save_ip_data(ip_data):
    with open(DATA_FILE, "w") as f:
        json.dump(ip_data, f, indent=4)


# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Server Monitoring Dashboard"
server = app.server

# Load initial IP data
initial_ip_data = load_ip_data()
initial_ip_list = list(initial_ip_data.keys())

# App layout with initialized stores
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="ip-store", data=initial_ip_list),
        dcc.Store(id="ip-data-store", data=initial_ip_data),
        dcc.Store(id="historical-data-store", data={}),
        dcc.Store(id="ip-locations-store", data={}),
        dcc.Store(id="current-view", data="main"),
        html.Div(html.Img(src="/assets/logo.png", className="logo")),
        html.Div(id="page-content", children=main_dashboard_layout(initial_ip_list)),
        dcc.Interval(id="interval-component-main", interval=5 * 1000, n_intervals=0),
    ]
)


@app.callback(
    [
        Output("page-content", "children"),
        Output("current-view", "data"),
        Output("interval-component-main", "disabled"),
        Output("interval-component-server", "disabled"),
    ],
    [Input("url", "pathname")],
    [State("ip-store", "data")],
)
def display_page(pathname, ip_list):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        ip = urllib.parse.unquote(ip)
        if ip in ip_list:
            return server_dashboard_layout(ip_list, ip), "server", True, False
    return main_dashboard_layout(ip_list), "main", False, True


@app.callback(
    Output("interval-component-server", "interval", allow_duplicate=True),
    [Input("set-refresh-rate", "n_clicks")],
    [State("refresh-rate-slider", "value"), State("current-view", "data")],
    prevent_initial_call=True,
)
def update_server_interval(n_clicks, value, current_view):
    if current_view != "server":
        raise PreventUpdate
    if n_clicks > 0:
        return value * 1000
    return no_update


@app.callback(
    [
        Output("ip-input", "value"),
        Output("ip-store", "data"),
        Output("ip-data-store", "data"),
        Output("server-table-body", "children"),
    ],
    [
        Input("add-button", "n_clicks"),
        Input("interval-component-main", "n_intervals"),
        Input({"type": "delete-button", "ip": ALL}, "n_clicks"),
    ],
    [
        State("ip-input", "value"),
        State("ip-store", "data"),
        State("ip-data-store", "data"),
        State("current-view", "data"),
    ],
    prevent_initial_call=True,
)
def manage_ip_addresses(
    add_clicks, n_intervals, delete_clicks, ip, ip_list, ip_data, current_view
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"]

    # Only process interval updates if we're on main dashboard
    if "interval-component-main" in triggered_id and current_view != "main":
        raise PreventUpdate

    # Handle delete button
    if "delete-button" in triggered_id:
        try:
            # Extract everything between the first { and the last }
            import re

            json_match = re.search(r"({.+})", triggered_id)
            if json_match:
                button_id = json_match.group(1)
                button_data = json.loads(button_id)
                encoded_ip = button_data.get("ip")
                if encoded_ip:
                    ip_to_delete = urllib.parse.unquote(encoded_ip)
                    print(f"Attempting to delete IP: {ip_to_delete}")

                    if ip_to_delete in ip_list:
                        ip_list.remove(ip_to_delete)
                        ip_data.pop(ip_to_delete, None)
                        save_ip_data(ip_data)
                        rows = create_table_rows(ip_list, ip_data)
                        if not rows:
                            rows = [
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
                        return ["", ip_list, ip_data, rows]
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(
                f"Problem string: {button_id if 'button_id' in locals() else 'No button_id'}"
            )
            return [no_update, no_update, no_update, no_update]
        except Exception as e:
            print(f"Error deleting IP: {e}")
            print(f"Full triggered_id: {triggered_id}")
            return [no_update, no_update, no_update, no_update]

    # Handle IP addition
    if "add-button" in triggered_id:
        if not ip or ip in ip_list:
            raise PreventUpdate

        ip_list.append(ip)
        ip_data[ip] = {
            "health": "Fetching...",
            "processor_name": "Fetching...",
            "number_of_cores": "Fetching...",
            "frequency": "Fetching...",
            "connected_users": "Fetching...",
        }
        save_ip_data(ip_data)
        rows = create_table_rows(ip_list, ip_data)
        if not rows:
            rows = [
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
        return ["", ip_list, ip_data, rows]

    # Handle interval updates
    if "interval-component-main" in triggered_id:
        for ip_addr in ip_list:
            if ip_addr not in ip_data:
                ip_data[ip_addr] = {
                    "health": "Fetching...",
                    "processor_name": "Fetching...",
                    "number_of_cores": "Fetching...",
                    "frequency": "Fetching...",
                    "connected_users": "Fetching...",
                }
            else:
                try:
                    set_base_url(ip_addr)
                    data = asyncio.run(fetch_all_data())
                    ip_data[ip_addr]["health"] = data.get(
                        "health_status", "Not Reachable"
                    )
                    cpu_core_info = data.get("cpu_core_info", {})
                    ip_data[ip_addr]["processor_name"] = cpu_core_info.get(
                        "processor_name", "N/A"
                    )
                    ip_data[ip_addr]["number_of_cores"] = cpu_core_info.get(
                        "number_of_cores", "N/A"
                    )
                    ip_data[ip_addr]["frequency"] = cpu_core_info.get(
                        "frequency", "N/A"
                    )
                    ip_data[ip_addr]["connected_users"] = data.get(
                        "last_connected", "N/A"
                    )
                except Exception as e:
                    print(f"Error updating IP {ip_addr}: {e}")

        save_ip_data(ip_data)
        rows = create_table_rows(ip_list, ip_data)
        if not rows:
            rows = [
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
        return [no_update, ip_list, ip_data, rows]

    return [no_update, no_update, no_update, no_update]


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    [
        Input({"type": "ip-link", "ip": ALL}, "n_clicks"),
        Input("ip-switcher", "value"),
        Input("back-button", "n_clicks"),
        Input({"type": "retry-button", "index": ALL}, "n_clicks"),
    ],
    State("ip-store", "data"),
    State("ip-data-store", "data"),
    prevent_initial_call=True,
)
def handle_navigation(
    ip_link_clicks, selected_ip, back_clicks, retry_clicks, ip_list, ip_data
):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if "ip-link" in triggered_id and any(ip_link_clicks):
        button_data = ast.literal_eval(triggered_id)
        ip = urllib.parse.unquote(button_data["ip"])  # Decode the IP
        return f"/server/{ip}"

    elif "back-button" in triggered_id and back_clicks:
        return "/"

    elif "ip-switcher" in triggered_id and selected_ip:
        return f"/server/{selected_ip}"

    elif "retry-button" in triggered_id and any(retry_clicks):
        button_data = ast.literal_eval(triggered_id)
        ip = urllib.parse.unquote(button_data["index"])  # Decode the IP
        return no_update

    raise PreventUpdate


@app.callback(
    Output("health-status", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
)
def update_health_status(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        ip = urllib.parse.unquote(ip)  # Properly decode the IP address
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        health = data.get("health_status", "Not Reachable")
        color = "green" if health == "Reachable" else "red"
        return html.Span(health, style={"color": color, "fontSize": "1.5rem"})
    return no_update


@app.callback(
    Output("cpu-core-info", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
)
def update_cpu_core_info(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        cpu_core_info = data.get("cpu_core_info", {})
        
        processor_name = cpu_core_info.get('processor_name', 'Unavailable')
        number_of_cores = cpu_core_info.get('number_of_cores', 'Unavailable')
        frequency = cpu_core_info.get('frequency', 'Unavailable')
        
        return html.Div([
            html.P(f"Processor Name: {processor_name}"),
            html.P(f"Number of Cores: {number_of_cores}"),
            html.P(f"Frequency: {frequency} MHz" if frequency != 'Unavailable' else "Frequency: Unavailable"),
        ])
    return no_update


@app.callback(
    [
        Output("cpu-graph", "figure", allow_duplicate=True),
        Output("ram-graph", "figure", allow_duplicate=True),
        Output("historical-data-store", "data", allow_duplicate=True),
    ],
    Input("interval-component-server", "n_intervals"),
    [
        State("url", "pathname"),
        State("historical-data-store", "data"),
        State("current-view", "data"),
    ],
    prevent_initial_call=True,
)
def update_graphs_data(n_intervals, pathname, historical_data_store, current_view):
    if current_view != "server":
        raise PreventUpdate

    if not pathname or not pathname.startswith("/server/"):
        raise PreventUpdate

    try:
        ip = pathname.split("/server/")[1]
        ip = urllib.parse.unquote(ip)
        set_base_url(ip)

        # Fetch CPU and RAM data
        data = asyncio.run(fetch_all_data())
        cpu_data = data.get("cpu_data", [])
        ram_data = data.get("ram_data", {})

        # Update graphs
        cpu_fig = update_cpu_graph(cpu_data)
        ram_fig = update_ram_graph(ram_data)

        # Update historical data
        historical_data = historical_data_store or {}
        timestamp = time.time()

        if ip not in historical_data:
            historical_data[ip] = {"cpu": [], "ram": []}

        historical_data[ip]["cpu"].append(
            (
                timestamp,
                (
                    sum(float(core["usage"]) for core in cpu_data) / len(cpu_data)
                    if cpu_data
                    else 0
                ),
            )
        )
        historical_data[ip]["ram"].append(
            (
                timestamp,
                (
                    (
                        ram_data.get("used", 0)
                        / (ram_data.get("used", 0) + ram_data.get("available", 1))
                        * 100
                    )
                    if ram_data
                    else 0
                ),
            )
        )

        return cpu_fig, ram_fig, historical_data

    except Exception as e:
        print(f"Error updating graphs: {e}")
        raise PreventUpdate


@app.callback(
    Output("interval-component-server", "interval"),
    Input("set-refresh-rate", "n_clicks"),
    State("refresh-rate-slider", "value"),
)
def update_interval(n_clicks, value):
    if n_clicks > 0:
        return value * 1000  # Convert seconds to milliseconds
    return no_update


@app.callback(
    Output("disk-graph", "figure"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
)
def update_disk_graph_data(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        disk_data = data.get("disk_data", {})
        return update_disk_graph(disk_data)
    return go.Figure()


@app.callback(
    Output("historical-cpu-graph", "figure"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
    State("historical-data-store", "data"),
)
def update_historical_cpu_graph_data(n_intervals, pathname, historical_data_store):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        historical_cpu_data = historical_data_store.get(ip, {}).get("cpu", [])
        return update_historical_cpu_graph(historical_cpu_data)
    return go.Figure()


@app.callback(
    Output("historical-ram-graph", "figure"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
    State("historical-data-store", "data"),
)
def update_historical_ram_graph_data(n_intervals, pathname, historical_data_store):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        historical_ram_data = historical_data_store.get(ip, {}).get("ram", [])
        return update_historical_ram_graph(historical_ram_data)
    return go.Figure()


@app.callback(
    Output("log-data", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
)
def update_log_data(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        log_data = data.get("log_data", {})
        return log_layout(log_data)
    return no_update


@app.callback(
    Output("aggregated-log-data", "children"),
    Input("interval-component-main", "n_intervals"),
    State("ip-store", "data"),
)
def update_aggregated_log_data(n_intervals, ip_list):
    if not ip_list:
        raise PreventUpdate

    aggregated_data = {"failed": 0, "succeed": 0, "total_visitors": 0}

    for ip in ip_list:
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        log_data = data.get("log_data", {})

        aggregated_data["failed"] += log_data.get("failed", 0)
        aggregated_data["succeed"] += log_data.get("succeed", 0)
        aggregated_data["total_visitors"] += sum(
            log_data.get("nbwebsites", {}).values()
        )

    return aggregated_log_layout(aggregated_data)


@app.callback(
    Output("average-usage", "children"),
    Input("interval-component-main", "n_intervals"),
    State("ip-store", "data"),
)
def update_average_usage(n_intervals, ip_list):
    if not ip_list:
        raise PreventUpdate

    total_cpu_usage = 0
    total_ram_usage = 0
    count = 0

    for ip in ip_list:
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        cpu_data = data.get("cpu_data", [])
        ram_data = data.get("ram_data", {})

        if cpu_data:
            total_cpu_usage += sum(float(core["usage"]) for core in cpu_data) / len(
                cpu_data
            )
        if ram_data:
            total_ram_usage += (
                ram_data.get("used", 0)
                / (ram_data.get("used", 0) + ram_data.get("available", 1))
                * 100
            )

        count += 1

    if count == 0:
        return "No data available"

    avg_cpu_usage = total_cpu_usage / count
    avg_ram_usage = total_ram_usage / count

    return html.Div(
        [
            html.P(
                f"Average CPU Usage: {avg_cpu_usage:.2f}%",
                className="average-usage-text",
            ),
            html.P(
                f"Average RAM Usage: {avg_ram_usage:.2f}%",
                className="average-usage-text",
            ),
        ]
    )


@app.callback(
    Output("recent-logs", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
)
def update_recent_logs(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        recent_logs = data.get("recent_logs", [])
        return recent_logs_layout(recent_logs)
    return no_update


@app.callback(
    Output("ip-map", "children"),
    Output("ip-map-message", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
    State("ip-locations-store", "data"),
)
def update_ip_map(n_intervals, pathname, ip_locations_store):
    if not pathname or not pathname.startswith("/server/"):
        return no_update, no_update

    try:
        ip = pathname.split("/server/")[1]
        ip = urllib.parse.unquote(ip)  # Properly decode the IP address
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        ip_visits = data.get("log_data", {}).get("ip_visits", {})

        if not ip_visits:
            return (
                html.Div(
                    [
                        html.H4(
                            "IP Location Map",
                            style={"textAlign": "center", "color": "gray"},
                        ),
                        html.P(
                            "No IP visit data available",
                            style={"textAlign": "center", "color": "gray"},
                        ),
                    ]
                ),
                no_update,
            )

        # Only fetch locations for new IPs
        new_locations = False
        for visit_ip in ip_visits.keys():
            if visit_ip not in ip_locations_store:
                location = asyncio.run(fetch_geolocation(visit_ip))
                if location:
                    ip_locations_store[visit_ip] = location
                    new_locations = True

        # Check if there are only private IPs
        public_ips = {
            ip: loc for ip, loc in ip_locations_store.items() if loc is not None
        }
        if not public_ips:
            # Add mock IP locations
            mock_ips = ["34.21.9.50", "34.106.208.213", "34.240.49.81", "13.70.181.210"]
            for mock_ip in mock_ips:
                if mock_ip not in ip_locations_store:
                    location = asyncio.run(fetch_geolocation(mock_ip))
                    if location:
                        ip_locations_store[mock_ip] = location
                        new_locations = True

            return map_layout(ip_locations_store), html.P(
                "Server only contains private IP addresses. Check proxy settings.",
                style={"textAlign": "center", "color": "red"},
            )

        # Only update if we have new locations
        if new_locations or not ip_locations_store:
            return map_layout(ip_locations_store), no_update
        return no_update, no_update

    except Exception as e:
        return (
            html.Div(
                [
                    html.H4(
                        "IP Location Map", style={"textAlign": "center", "color": "red"}
                    ),
                    html.P(
                        f"Error: {str(e)}",
                        style={"textAlign": "center", "color": "red"},
                    ),
                ]
            ),
            no_update,
        )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
