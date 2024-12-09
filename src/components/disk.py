from dash import dcc, html
import plotly.graph_objs as go
from services.api_service import fetch_disk_data

# src/components/disk.py
def update_disk_graph(disk_data):
    if not disk_data:
        return go.Figure(layout=go.Layout(title="Disk Usage - No Data Available"))

    # Extract values and convert bytes to GB
    used_gb = disk_data.get("used", 0) / (1024 ** 3)
    free_gb = disk_data.get("free", 0) / (1024 ** 3)

    # Prepare figure
    figure = {
        "data": [
            go.Bar(
                x=["Used", "Free"],
                y=[used_gb, free_gb],
                text=[f"{used_gb:.2f} GB", f"{free_gb:.2f} GB"],
                textposition="auto",
                marker=dict(color=["#636EFA", "#EF553B"]),
            )
        ],
        "layout": go.Layout(
            title="Disk Usage",
            xaxis={"title": "Metrics"},
            yaxis={"title": "Size (GB)"},
            height=350,
        )
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