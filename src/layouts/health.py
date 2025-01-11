# health.py
from dash import html


def health_layout():
    return html.Div(
        [
            html.H2(
                "Health Status", style={"textAlign": "center", "marginBottom": "10px"}
            ),
            html.Div(id="health-status", style={"textAlign": "center"}),
        ]
    )
