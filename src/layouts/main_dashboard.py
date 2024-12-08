# src/layouts/main_dashboard.py
from dash import html, dcc

def main_dashboard_layout(ip_list):
    # Create initial table rows
    initial_rows = create_table_rows(ip_list, {})

    return html.Div([
        html.H1("Server Monitoring Dashboard", style={"textAlign": "center"}),

        # Input field and add button
        html.Div([
            dcc.Input(
                id='ip-input',  # Ensure this ID matches the callback
                type='text',
                placeholder='Enter IP Address',
                style={'marginRight': '10px'}
            ),
            html.Button(
                'Add',
                id='add-button',  # Ensure this ID matches the callback
                n_clicks=0,
                className='add-button'
            )
        ], style={"textAlign": "center", "marginBottom": "20px"}),

        # Server table
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("IP Address"),
                    html.Th("Health"),
                    html.Th("Processor Name"),
                    html.Th("Number of Cores"),
                    html.Th("Frequency (MHz)"),
                    html.Th("Actions")
                ])
            ]),
            html.Tbody(id="server-table-body", children=initial_rows)
        ], className="styled-table"),

        # Average CPU and RAM usage
        html.Div([
            html.H3("Average CPU and RAM Usage", style={"textAlign": "center"}),
            html.Div(id="average-usage", className="average-usage")
        ]),

        # Hidden elements for callbacks
        dcc.Dropdown(
            id='ip-switcher',
            options=[{'label': ip, 'value': ip} for ip in ip_list],
            style={'display': 'none'}
        ),
        html.Button(
            'Back to Dashboard',
            id='back-button',
            n_clicks=0,
            style={'display': 'none'}
        )
    ])

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