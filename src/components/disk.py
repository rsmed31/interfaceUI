from dash import dcc, html
import plotly.graph_objs as go
from services.api_service import fetch_disk_data

def update_disk_graph():
    """Fetch and return Disk usage graph data."""
    disk_data = fetch_disk_data()
    if not disk_data:  # Fallback if API response is empty
        disk_data = {"total": 0, "used": 0, "free": 0}

    # Convert bytes to gigabytes
    used_gb = round(disk_data["used"] / (1024 ** 3), 2)
    free_gb = round(disk_data["free"] / (1024 ** 3), 2)

    # Create the figure
    figure = {
        "data": [
            go.Bar(
                x=["Used", "Free"],
                y=[used_gb, free_gb],
                text=[f"{used_gb} GB", f"{free_gb} GB"],
                textposition="auto",
                marker=dict(color=["#636EFA", "#EF553B"]),
            )
        ],
        "layout": go.Layout(
            title={"text": "Disk Usage", "x": 0.5},
            xaxis={"title": "Metrics", "showgrid": False},
            yaxis={"title": "Size (GB)", "showgrid": True},
            margin={"l": 30, "r": 30, "t": 50, "b": 50},
            height=350,
        ),
    }
    return figure

def disk_layout():
    """Return layout for Disk section."""
    return html.Div(
        [
            html.H4(
                "Disk Usage",
                style={
                    "textAlign": "center",
                    "color": "blue",
                    "marginBottom": "10px",
                },
            ),
            dcc.Graph(
                id="disk-graph",
                className="dccGraph",  # Add class for consistent styling
            ),
        ],
        className="graph-container",
        style={
            "flex": 1,
            "padding": "10px",
            "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
            "borderRadius": "10px",
            "height": "100%",  # Ensure the container takes full height
        },
    )