# src/layouts/server_dashboard.py
from dash import html, dcc
from components.cpu import cpu_layout
from components.disk import disk_layout
from components.ram import ram_layout
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

        # Graph sections
        html.Div([
            html.Div(cpu_layout(), className="graph-container"),
            html.Div(disk_layout(), className="graph-container"),
            html.Div(ram_layout(), className="graph-container"),
        ], className="graph-section", style={
            "display": "flex",
            "justifyContent": "space-around",
            "gap": "20px"
        }),

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