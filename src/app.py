import asyncio
import urllib.parse
from dash import Dash, dcc, html, no_update, callback_context
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from components.cpu import update_cpu_graph, update_historical_cpu_graph
from components.ram import update_ram_graph, update_historical_ram_graph
from components.disk import update_disk_graph
from components.logs import log_layout, aggregated_log_layout, recent_logs_layout
from services.api_service import fetch_health_status, set_base_url, fetch_cpu_core_info, fetch_cpu_data, fetch_ram_data, fetch_disk_data, fetch_all_data
from layouts.main_dashboard import main_dashboard_layout, create_table_rows
from layouts.server_dashboard import server_dashboard_layout
from layouts.health import health_layout
from datetime import datetime
import plotly.graph_objects as go 
from layouts.map import map_layout
from services.api_service import fetch_geolocation

# Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Server Monitoring Dashboard"
server = app.server

# App layout with initialized ip_data_store
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='ip-store', data=["localhost:8000"]),
    dcc.Store(id='ip-data-store', data={
        "localhost:8000": {
            'health': 'Fetching...',
            'processor_name': 'Fetching...',
            'number_of_cores': 'Fetching...',
            'frequency': 'Fetching...'     ,
            'connected_users': 'Fetching...'
        }
    }),
    dcc.Store(id='historical-data-store', data={}),
    dcc.Store(id='ip-locations-store', data={}),
    html.Div(id='page-content', children=main_dashboard_layout(["localhost:8000"])),
    dcc.Interval(id='interval-component-main', interval=5*1000, n_intervals=0),
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('ip-store', 'data')
)
def display_page(pathname, ip_list):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        ip = urllib.parse.unquote(ip)
        if ip in ip_list:
            return server_dashboard_layout(ip_list, ip)
    return main_dashboard_layout(ip_list)

@app.callback(
    Output('ip-input', 'value'),
    Output('ip-store', 'data'),
    Output('ip-data-store', 'data'),
    Output('server-table-body', 'children'),
    Input('add-button', 'n_clicks'),
    Input('interval-component-main', 'n_intervals'),
    State('ip-input', 'value'),
    State('ip-store', 'data'),
    State('ip-data-store', 'data')
)
def add_ip_address(n_clicks, n_intervals, ip, ip_list, ip_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle IP addition
    if triggered_id == 'add-button':
        if not ip or ip in ip_list:
            raise PreventUpdate

        ip_list.append(ip)
        ip_data[ip] = {
            'health': 'Fetching...',
            'processor_name': 'Fetching...',
            'number_of_cores': 'Fetching...',
            'frequency': 'Fetching...',
            'connected_users': 'Fetching...'  # Add this line
        }

        # Create table rows immediately
        rows = create_table_rows(ip_list, ip_data)
        return '', ip_list, ip_data, rows

    # Handle interval updates
    elif triggered_id == 'interval-component-main':
        # Update data for all IPs
        for ip_addr in ip_list:
            if ip_addr not in ip_data:
                ip_data[ip_addr] = {
                    'health': 'Fetching...',
                    'processor_name': 'Fetching...',
                    'number_of_cores': 'Fetching...',
                    'frequency': 'Fetching...',
                    'connected_users': 'Fetching...'  # Add this line
                }
            else:
                set_base_url(ip_addr)
                data = asyncio.run(fetch_all_data())
                ip_data[ip_addr]['health'] = data.get('health_status', 'Not Reachable')
                cpu_core_info = data.get('cpu_core_info', {})
                ip_data[ip_addr]['processor_name'] = cpu_core_info.get('processor_name', 'N/A')
                ip_data[ip_addr]['number_of_cores'] = cpu_core_info.get('number_of_cores', 'N/A')
                ip_data[ip_addr]['frequency'] = cpu_core_info.get('frequency', 'N/A')
                ip_data[ip_addr]['connected_users'] = data.get('last_connected', 'N/A')

        # Create table rows with updated data
        rows = create_table_rows(ip_list, ip_data)
        return no_update, ip_list, ip_data, rows

    return no_update, no_update, no_update, no_update

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input({'type': 'ip-link', 'ip': ALL}, 'n_clicks'),
     Input('ip-switcher', 'value'),
     Input('back-button', 'n_clicks'),
     Input({'type': 'retry-button', 'index': ALL}, 'n_clicks')],
    State('ip-store', 'data'),
    State('ip-data-store', 'data'),
    prevent_initial_call=True
)
def handle_navigation(ip_link_clicks, selected_ip, back_clicks, retry_clicks, ip_list, ip_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if 'ip-link' in triggered_id and any(ip_link_clicks):
        button_data = eval(triggered_id)
        ip = urllib.parse.unquote(button_data['ip'])
        return f"/server/{ip}"

    elif 'back-button' in triggered_id and back_clicks:
        return '/'

    elif 'ip-switcher' in triggered_id and selected_ip:
        return f"/server/{selected_ip}"

    elif 'retry-button' in triggered_id and any(retry_clicks):
        button_data = eval(triggered_id)
        ip = urllib.parse.unquote(button_data['index'])
        # Rest of the retry button logic...
        return no_update

    raise PreventUpdate

@app.callback(
    Output("health-status", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname")
)
def update_health_status(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        health = data.get("health_status", "Not Reachable")
        color = "green" if health == "Reachable" else "red"
        return html.Span(health, style={"color": color, "fontSize": "1.5rem"})
    return no_update

@app.callback(
    Output("cpu-core-info", "children"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname")
)
def update_cpu_core_info(n_intervals, pathname):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        cpu_core_info = data.get("cpu_core_info", {})
        if not cpu_core_info:
            return html.Div("CPU Core Info Not Available", style={"color": "red"})
        return html.Div([
            html.P(f"Processor Name: {cpu_core_info.get('processor_name', 'N/A')}"),
            html.P(f"Number of Cores: {cpu_core_info.get('number_of_cores', 'N/A')}"),
            html.P(f"Frequency: {cpu_core_info.get('frequency', 'N/A')} MHz")
        ])
    return no_update

@app.callback(
    Output("cpu-graph", "figure"),
    Output("ram-graph", "figure"),
    Output("historical-data-store", "data"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname"),
    State("historical-data-store", "data")
)
def update_graphs_data(n_intervals, pathname, historical_data_store):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        
        # Update CPU data
        cpu_data = data.get("cpu_data", [])
        timestamp = datetime.now().timestamp()
        total_cpu_usage = sum(float(core["usage"]) for core in cpu_data) / len(cpu_data) if cpu_data else 0
        if ip not in historical_data_store:
            historical_data_store[ip] = {"cpu": [], "ram": []}
        historical_data_store[ip]["cpu"].append({"timestamp": timestamp, "total_usage": total_cpu_usage})
        historical_data_store[ip]["cpu"] = historical_data_store[ip]["cpu"][-100:]  # Keep only the last 100 data points
        
        # Update RAM data
        ram_data = data.get("ram_data", {})
        used = ram_data.get("used", 0)
        total = used + ram_data.get("available", 0)
        total_ram_usage = (used / total) * 100 if total else 0
        historical_data_store[ip]["ram"].append({"timestamp": timestamp, "total_usage": total_ram_usage})
        historical_data_store[ip]["ram"] = historical_data_store[ip]["ram"][-100:]  # Keep only the last 100 data points
        
        return update_cpu_graph(cpu_data), update_ram_graph(ram_data), historical_data_store
    return no_update, no_update, historical_data_store

@app.callback(
    Output("disk-graph", "figure"),
    Input("interval-component-server", "n_intervals"),
    State("url", "pathname")
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
    Input("url", "pathname"),
    State("historical-data-store", "data")
)
def update_historical_cpu_graph_data(pathname, historical_data_store):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        historical_cpu_data = historical_data_store.get(ip, {}).get("cpu", [])
        return update_historical_cpu_graph(historical_cpu_data)
    return go.Figure()

@app.callback(
    Output("historical-ram-graph", "figure"),
    Input("url", "pathname"),
    State("historical-data-store", "data")
)
def update_historical_ram_graph_data(pathname, historical_data_store):
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        historical_ram_data = historical_data_store.get(ip, {}).get("ram", [])
        return update_historical_ram_graph(historical_ram_data)
    return go.Figure()

@app.callback(
    Output('log-data', 'children'),
    Input('interval-component-server', 'n_intervals'),
    State('url', 'pathname')
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
    Output('aggregated-log-data', 'children'),
    Input('interval-component-main', 'n_intervals'),
    State('ip-store', 'data')
)
def update_aggregated_log_data(n_intervals, ip_list):
    if not ip_list:
        raise PreventUpdate

    aggregated_data = {
        "failed": 0,
        "succeed": 0,
        "total_visitors": 0
    }

    for ip in ip_list:
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        log_data = data.get("log_data", {})

        aggregated_data["failed"] += log_data.get("failed", 0)
        aggregated_data["succeed"] += log_data.get("succeed", 0)
        aggregated_data["total_visitors"] += sum(log_data.get("nbwebsites", {}).values())

    return aggregated_log_layout(aggregated_data)

@app.callback(
    Output('average-usage', 'children'),
    Input('interval-component-main', 'n_intervals'),
    State('ip-store', 'data')
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
            total_cpu_usage += sum(float(core["usage"]) for core in cpu_data) / len(cpu_data)
        if ram_data:
            total_ram_usage += ram_data.get("used", 0) / (ram_data.get("used", 0) + ram_data.get("available", 1)) * 100

        count += 1

    if count == 0:
        return "No data available"

    avg_cpu_usage = total_cpu_usage / count
    avg_ram_usage = total_ram_usage / count

    return html.Div([
        html.P(f"Average CPU Usage: {avg_cpu_usage:.2f}%", className="average-usage-text"),
        html.P(f"Average RAM Usage: {avg_ram_usage:.2f}%", className="average-usage-text")
    ])

@app.callback(
    Output('recent-logs', 'children'),
    Input('interval-component-server', 'n_intervals'),
    State('url', 'pathname')
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
    Output('ip-map', 'children'),
    Input('interval-component-server', 'n_intervals'),
    State('url', 'pathname'),
    State('ip-locations-store', 'data')
)
def update_ip_map(n_intervals, pathname, ip_locations_store):
    if not pathname or not pathname.startswith("/server/"):
        return no_update

    try:
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        data = asyncio.run(fetch_all_data())
        ip_visits = data.get("log_data", {}).get("ip_visits", {})

        if not ip_visits:
            return html.Div([
                html.H4("IP Location Map", style={"textAlign": "center", "color": "gray"}),
                html.P("No IP visit data available", 
                      style={"textAlign": "center", "color": "gray"})
            ])

        # Only fetch locations for new IPs
        new_locations = False
        for visit_ip in ip_visits.keys():
            if visit_ip not in ip_locations_store:
                location = asyncio.run(fetch_geolocation(visit_ip))
                if location:
                    ip_locations_store[visit_ip] = location
                    new_locations = True

        # Only update if we have new locations
        if new_locations or not ip_locations_store:
            return map_layout(ip_locations_store)
        return no_update

    except Exception as e:
        return html.Div([
            html.H4("IP Location Map", style={"textAlign": "center", "color": "red"}),
            html.P(f"Error: {str(e)}", 
                  style={"textAlign": "center", "color": "red"})
        ])

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
