from dash import html
from components.cpu import cpu_layout
from components.disk import disk_layout
from components.ram import ram_layout
from layouts.health import health_layout

def dashboard_layout():
    """Main dashboard layout."""
    return html.Div([
        health_layout(),
        html.Div(
            [
                html.Div(cpu_layout(), style={"flex": "1", "margin": "10px"}),
                html.Div(disk_layout(), style={"flex": "1", "margin": "10px"}),
                html.Div(ram_layout(), style={"flex": "1", "margin": "10px"})
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "space-between",
                "alignItems": "flex-start",
                "marginTop": "20px"
            }
        )
    ])
