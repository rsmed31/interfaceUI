from dash import html

def header_layout():
    """Header layout for the dashboard."""
    return html.Div([
        html.H1(
            "Server Monitoring Dashboard",
            style={"textAlign": "center", "marginBottom": "20px", "fontSize": "2rem"}
        )
    ])
