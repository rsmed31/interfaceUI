from dash import html, dcc
from components.logs import aggregated_log_layout
import urllib.parse

def main_dashboard_layout(ip_list):
    return html.Div([
        html.H1("Server Monitoring Dashboard", className="text-center mb-20"),

        # Input container
        html.Div([
            dcc.Input(
                id='ip-input',
                type='text',
                placeholder='Enter IP Address',
                className='ip-input'
            ),
            html.Button(
                'Add',
                id='add-button',
                n_clicks=0,
                className='add-button'
            )
        ], className="text-center mb-20"),

        # Server table in card container
        html.Div([
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("IP Address"),
                        html.Th("Health"),
                        html.Th("Processor Name"),
                        html.Th("Number of Cores"),
                        html.Th("Frequency (MHz)"),
                        html.Th("Connected Users"),
                        html.Th("Actions")
                    ])
                ]),
                html.Tbody(id="server-table-body", children=create_table_rows(ip_list, {}))
            ], className="styled-table")
        ], className="card"),

        # Stats cards
        html.Div([
            # Aggregated log data
            html.Div(id='aggregated-log-data', className="card"),
            
            # Average usage
            html.Div([
                html.H3("Average Usage", className="text-center mb-20"),
                html.Div(id="average-usage", className="average-usage")
            ], className="card")
        ], className="grid-container"),

        # Hidden elements
        dcc.Dropdown(id='ip-switcher', style={'display': 'none'}),
        html.Button(id='back-button', style={'display': 'none'})
    ], className="dashboard-container")

def create_table_rows(ip_list, ip_data):
    """Helper function to create table rows"""
    rows = []
    for ip in ip_list:
        if ip not in ip_data:
            ip_data[ip] = {
                'health': 'Fetching...',
                'processor_name': 'Fetching...',
                'number_of_cores': 'Fetching...',
                'frequency': 'Fetching...',
                'connected_users': 'Fetching...'
            }
            
        data = ip_data[ip]
        # Don't encode the IP for display, only for the href
        rows.append(html.Tr([
            html.Td(dcc.Link(
                ip,
                href=f"/server/{ip}",
                style={
                    'color': 'blue',
                    'textDecoration': 'underline',
                    'cursor': 'pointer'
                }
            )),
            html.Td(data['health']),
            html.Td(data['processor_name']),
            html.Td(data['number_of_cores']),
            html.Td(data['frequency']),
            html.Td(data['connected_users']),
            html.Td(html.Button('Retry', id={'type': 'retry-button', 'index': ip}, n_clicks=0))
        ]))
    return rows