from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from components.cpu import cpu_layout, update_cpu_graph
from components.ram import ram_layout, update_ram_graph
from components.disk import disk_layout, update_disk_graph
from services.api_service import fetch_health_status

# Initialize the Dash app
app = Dash(__name__)
app.title = "Server Monitoring Dashboard"
server = app.server

# App layout
app.layout = html.Div([
    html.H1("Server Monitoring Dashboard", style={"textAlign": "center"}),
    html.H3("Health Status", style={"textAlign": "center"}),
    html.Div(id="health-status", style={"textAlign": "center", "marginBottom": "20px"}),

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

# Callbacks for health status
@app.callback(
    Output("health-status", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_health_status(n_intervals):
    status = fetch_health_status()
    if status == "Reachable":
        return html.Span("Reachable", style={"color": "green", "fontWeight": "bold"})
    else:
        return html.Span("Not Reachable", style={"color": "red", "fontWeight": "bold"})

# Callback for CPU graph
@app.callback(
    Output("cpu-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_cpu_graph_data(n_intervals):
    return update_cpu_graph()

# Callback for Disk graph
@app.callback(
    Output("disk-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_disk_graph_data(n_intervals):
    return update_disk_graph()

# Callback for RAM graph
@app.callback(
    Output("ram-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_ram_graph_data(n_intervals):
    return update_ram_graph()

if __name__ == "__main__":
    app.run_server(debug=True)