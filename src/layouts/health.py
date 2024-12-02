from dash import html

def health_layout():
    """Health status section layout with placeholder."""
    return html.Div([
        html.H2(
            "Health Status",
            style={
                "textAlign": "center",
                "marginBottom": "10px",
                "fontSize": "1.5rem",
                "fontWeight": "bold"
            }
        ),
        html.Div(
            id="health-status",
            children="Not Reachable",  # Initial placeholder text
            style={
                "textAlign": "center",
                "fontSize": "1.5rem",
                "fontWeight": "bold",
                "color": "red",  # Placeholder starts as red
                "padding": "10px",
                "border": "2px solid #ddd",
                "borderRadius": "5px",
                "margin": "10px auto",
                "width": "200px",
                "backgroundColor": "#f9f9f9"
            }
        )
    ], style={"marginTop": "20px"})
