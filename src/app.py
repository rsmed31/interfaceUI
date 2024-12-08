# src/app.py
from dash import Dash, dcc, html, no_update, callback_context
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from components.cpu import update_cpu_graph
from components.ram import update_ram_graph
from components.disk import update_disk_graph
from services.api_service import fetch_health_status, set_base_url, fetch_cpu_core_info, fetch_cpu_data, fetch_ram_data, fetch_disk_data
from layouts.main_dashboard import main_dashboard_layout
from layouts.server_dashboard import server_dashboard_layout
from layouts.health import health_layout

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
            'frequency': 'Fetching...'
        }
    }),
    html.Div(id='page-content', children=main_dashboard_layout(["localhost:8000"])),
    dcc.Interval(id='interval-component-main', interval=20*1000, n_intervals=0),
    dcc.Interval(id='interval-component-server', interval=5*1000, n_intervals=0)
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
            'frequency': 'Fetching...'
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
                    'frequency': 'Fetching...'
                }
            else:
                set_base_url(ip_addr)
                ip_data[ip_addr]['health'] = fetch_health_status()
                cpu_core_info = fetch_cpu_core_info()
                ip_data[ip_addr]['processor_name'] = cpu_core_info.get('processor_name', 'N/A')
                ip_data[ip_addr]['number_of_cores'] = cpu_core_info.get('number_of_cores', 'N/A')
                ip_data[ip_addr]['frequency'] = cpu_core_info.get('frequency', 'N/A')

        # Create table rows with updated data
        rows = create_table_rows(ip_list, ip_data)
        return no_update, ip_list, ip_data, rows

    return no_update, no_update, no_update, no_update

def create_table_rows(ip_list, ip_data):
    """Helper function to create table rows"""
    rows = []
    for ip in ip_list:
        # Ensure IP exists in ip_data
        if ip not in ip_data:
            ip_data[ip] = {
                'health': 'Fetching...',
                'processor_name': 'Fetching...',
                'number_of_cores': 'Fetching...',
                'frequency': 'Fetching...'
            }

        data = ip_data[ip]
        rows.append(html.Tr([
            html.Td(html.Button(
                ip,
                id={'type': 'ip-link', 'ip': ip},
                n_clicks=0,
                style={
                    'background': 'none',
                    'border': 'none',
                    'color': 'blue',
                    'textDecoration': 'underline',
                    'cursor': 'pointer'
                }
            )),
            html.Td(data['health']),
            html.Td(data['processor_name']),
            html.Td(data['number_of_cores']),
            html.Td(data['frequency']),
            html.Td(html.Button('Retry', id={'type': 'retry-button', 'index': ip}, n_clicks=0))
        ]))
    return rows

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
        button_data = eval(triggered_id.split('.')[0])
        return f"/server/{button_data['ip']}"
    elif 'back-button' in triggered_id and back_clicks:
        return '/'
    elif 'ip-switcher' in triggered_id and selected_ip:
        return f"/server/{selected_ip}"
    elif 'retry-button' in triggered_id and any(retry_clicks):
        button_data = eval(triggered_id.split('.')[0])
        ip = button_data['index']
        ip_data[ip]['health'] = 'Fetching...'
        ip_data[ip]['processor_name'] = 'Fetching...'
        ip_data[ip]['number_of_cores'] = 'Fetching...'
        ip_data[ip]['frequency'] = 'Fetching...'
        set_base_url(ip)
        ip_data[ip]['health'] = fetch_health_status()
        cpu_core_info = fetch_cpu_core_info()
        ip_data[ip]['processor_name'] = cpu_core_info.get('processor_name', 'N/A')
        ip_data[ip]['number_of_cores'] = cpu_core_info.get('number_of_cores', 'N/A')
        ip_data[ip]['frequency'] = cpu_core_info.get('frequency', 'N/A')
        rows = create_table_rows(ip_list, ip_data)
        return no_update, ip_list, ip_data, rows

    return no_update

@app.callback(
    Output("health-status", "children"),
    Input("interval-component-server", "n_intervals"),
    State('url', 'pathname')
)
def update_health_status(n_intervals, pathname):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        health = fetch_health_status()
        color = "green" if health == "Reachable" else "red"
        return html.Span(health, style={"color": color, "fontSize": "1.5rem"})
    return no_update

@app.callback(
    Output("cpu-core-info", "children"),
    [Input("interval-component-server", "n_intervals")],
    [State("url", "pathname")]
)
def update_cpu_core_info(n_intervals, pathname):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        cpu_core_info = fetch_cpu_core_info()
        return html.Div([
            html.P(f"Processor Name: {cpu_core_info.get('processor_name', 'N/A')}"),
            html.P(f"Number of Cores: {cpu_core_info.get('number_of_cores', 'N/A')}"),
            html.P(f"Frequency: {cpu_core_info.get('frequency', 'N/A')} MHz")
        ])
    return no_update

@app.callback(
    Output("cpu-graph", "figure"),
    [Input("interval-component-server", "n_intervals")],
    [State("url", "pathname")]
)
def update_cpu_graph_data(n_intervals, pathname):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        return update_cpu_graph()
    return no_update

@app.callback(
    Output("disk-graph", "figure"),
    [Input("interval-component-server", "n_intervals")],
    [State("url", "pathname")]
)
def update_disk_graph_data(n_intervals, pathname):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        return update_disk_graph()
    return no_update

@app.callback(
    Output("ram-graph", "figure"),
    [Input("interval-component-server", "n_intervals")],
    [State("url", "pathname")]
)
def update_ram_graph_data(n_intervals, pathname):
    if isinstance(pathname, list):
        pathname = pathname[0]
    if pathname and pathname.startswith("/server/"):
        ip = pathname.split("/server/")[1]
        set_base_url(ip)
        return update_ram_graph()
    return no_update

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
        cpu_data = fetch_cpu_data()
        ram_data = fetch_ram_data()

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

if __name__ == "__main__":
    app.run_server(debug=True)