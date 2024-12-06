from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output, State
from components.cpu import cpu_layout, update_cpu_graph
from components.ram import ram_layout, update_ram_graph
from components.disk import disk_layout, update_disk_graph
from services.api_service import fetch_health_status, set_base_url

# Initialize the Dash app
app = Dash(__name__)
app.title = "Server Monitoring Dashboard"
server = app.server

# List of IP addresses to track
ip_addresses = ["http://localhost:8000", "http://192.168.1.1:8000", "http://192.168.1.2:8000"]

# App layout
app.layout = html.Div([
    html.H1("Server Monitoring Dashboard", style={"textAlign": "center"}),

    # Input field for adding IP addresses
    html.Div([
        html.Label("Add IP Address:", style={"marginRight": "10px"}),
        dcc.Input(id="ip-input", type="text", placeholder="Enter IP address", style={"width": "40%", "marginRight": "10px"}),
        html.Button("Add", id="add-ip-button", n_clicks=0, className="add-button")
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Spacer
    html.Div(style={"height": "20px"}),

    # Dropdown for selecting IP address
    html.Div([
        html.Label("Select IP Address:"),
        dcc.Dropdown(
            id="ip-dropdown",
            options=[{"label": ip, "value": ip} for ip in ip_addresses],
            value=ip_addresses[0],  # Default value
            clearable=False,
            style={"width": "50%", "margin": "0 auto"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Spacer
    html.Div(style={"height": "20px"}),

    html.H3("Health Status", style={"textAlign": "center"}),
    html.Div(id="health-status", style={"textAlign": "center", "marginBottom": "20px"}),

    # Spacer
    html.Div(style={"height": "20px"}),

    # Title for the plots
    html.H3("Realtime Tracker", style={"textAlign": "center", "marginBottom": "20px"}),

    # Graph sections with a flex layout for side-by-side graphs
    html.Div([
        html.Div(cpu_layout(), className="graph-container"),
        html.Div(disk_layout(), className="graph-container"),
        html.Div(ram_layout(), className="graph-container"),
    ], className="graph-section", style={"display": "flex", "justifyContent": "space-around", "gap": "20px"}),

    # Interval for periodic updates
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # 5 seconds
        n_intervals=0
    )
])

# Callback to add IP address
@app.callback(
    [Output("ip-dropdown", "options"), Output("ip-dropdown", "value")],
    [Input("add-ip-button", "n_clicks"), Input("ip-input", "n_submit")],
    [State("ip-input", "value"), State("ip-dropdown", "options")]
)
def add_ip_address(n_clicks, n_submit, new_ip, existing_options):
    if (n_clicks > 0 or n_submit) and new_ip:
        existing_options.append({"label": new_ip, "value": new_ip})
        return existing_options, new_ip
    return existing_options, no_update

# Callbacks for health status
@app.callback(
    Output("health-status", "children"),
    [Input("interval-component", "n_intervals")],
    [State("ip-dropdown", "value")]
)
def update_health_status(n_intervals, ip):
    set_base_url(ip)
    status = fetch_health_status()
    if status == "Reachable":
        return html.Span("Reachable", style={"color": "green", "fontWeight": "bold"})
    else:
        return html.Span("Not Reachable", style={"color": "red", "fontWeight": "bold"})

# Callback for CPU graph
@app.callback(
    Output("cpu-graph", "figure"),
    [Input("interval-component", "n_intervals")],
    [State("ip-dropdown", "value")]
)
def update_cpu_graph_data(n_intervals, ip):
    set_base_url(ip)
    return update_cpu_graph()

# Callback for Disk graph
@app.callback(
    Output("disk-graph", "figure"),
    [Input("interval-component", "n_intervals")],
    [State("ip-dropdown", "value")]
)
def update_disk_graph_data(n_intervals, ip):
    set_base_url(ip)
    return update_disk_graph()

# Callback for RAM graph
@app.callback(
    Output("ram-graph", "figure"),
    [Input("interval-component", "n_intervals")],
    [State("ip-dropdown", "value")]
)
def update_ram_graph_data(n_intervals, ip):
    set_base_url(ip)
    return update_ram_graph()

if __name__ == "__main__":
    app.run_server(debug=True)