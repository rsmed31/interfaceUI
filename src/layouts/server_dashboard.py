from dash import html, dcc
from components.cpu import cpu_layout, update_historical_cpu_graph
from components.disk import disk_layout
from components.ram import ram_layout, update_historical_ram_graph
from components.logs import log_layout  
from layouts.health import health_layout  

def server_dashboard_layout(ip_list, current_ip):
    return html.Div([
        html.H1(f"Server Dashboard: {current_ip}", style={"textAlign": "center"}),

        html.Div([
            html.Label('Switch Server:'),
            dcc.Dropdown(
                id='ip-switcher',
                options=[{'label': ip, 'value': ip} for ip in ip_list],
                value=current_ip,
                clearable=False
            )
        ], style={"textAlign": "center", "marginBottom": "20px"}),

        # Health status
        health_layout(),

        # Processor information
        html.Div(id="cpu-core-info", style={"textAlign": "center", "marginBottom": "20px"}),

        # Log data
        html.Div(id="log-data", className="log-data-container"),

        # Real-time Graph sections
        html.Div([
            html.Div(cpu_layout(), className="graph-container"),
            html.Div(disk_layout(), className="graph-container"),
            html.Div(ram_layout(), className="graph-container"),
        ], className="graph-section", style={
            "display": "flex",
            "justifyContent": "space-around",
            "gap": "20px"
        }),

        # Historical Graph sections
        html.Div([
            html.Div([
                html.H4("Historical CPU Usage", style={"textAlign": "center"}),
                dcc.Graph(id="historical-cpu-graph")
            ], className="graph-container"),
            html.Div([
                html.H4("Historical RAM Usage", style={"textAlign": "center"}),
                dcc.Graph(id="historical-ram-graph")
            ], className="graph-container"),
        ], className="graph-section", style={
            "display": "flex",
            "justifyContent": "space-around",
            "gap": "20px",
            "marginTop": "20px"
        }),

        # Recent Logs section
        html.Div(id='recent-logs', style={"marginTop": "20px"}),

        # Interval Component Moved Here
        dcc.Interval(id='interval-component-server', interval=5*1000, n_intervals=0),

        # Hidden add button
        html.Button(
            'Add',
            id='add-button',
            n_clicks=0,
            style={'display': 'none'}
        ),

        # Hidden ip-input
        dcc.Input(
            id='ip-input',
            type='text',
            style={'display': 'none'}
        ),

        # Hidden server-table-body
        html.Div(
            id='server-table-body',
            style={'display': 'none'}
        ),

        # Back button
        html.Div([
            html.Button(
                "Back to Dashboard",
                id="back-button",
                n_clicks=0,
                className="add-button"
            )
        ], style={"textAlign": "center", "marginTop": "20px"})
    ])