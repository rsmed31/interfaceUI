import plotly.graph_objs as go
from dash import dcc, html
from services.api_service import fetch_data
from datetime import datetime


def update_cpu_graph(cpu_data):
    """
    Update the CPU graph with the provided CPU data.

    Args:
        cpu_data (list): List of dictionaries containing CPU usage data.

    Returns:
        dict: Plotly figure dictionary for the CPU graph.
    """
    if not cpu_data:
        return go.Figure()
    x_data = [f"Core {core['id']}" for core in cpu_data]
    y_data = [float(core["usage"]) for core in cpu_data]
    return {
        "data": [
            go.Scatter(x=x_data, y=y_data, mode="lines+markers", name="CPU Usage")
        ],
        "layout": go.Layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(l=40, r=20, t=20, b=30),  # Add space on the left
            height=300,
            xaxis={"title": "Cores"},
            yaxis={"title": "Usage (%)", "range": [0, 100]},
        ),
    }


def update_historical_cpu_graph(historical_cpu_data):
    """
    Update the historical CPU graph with the provided historical CPU data.

    Args:
        historical_cpu_data (list): List of tuples containing timestamp and CPU usage data.

    Returns:
        dict: Plotly figure dictionary for the historical CPU graph.
    """
    if not historical_cpu_data:
        return go.Figure()

    x_data = [datetime.fromtimestamp(point[0]) for point in historical_cpu_data]
    y_data = [point[1] for point in historical_cpu_data]

    return {
        "data": [
            go.Scatter(
                x=x_data, y=y_data, mode="lines+markers", name="Historical CPU Usage"
            )
        ],
        "layout": go.Layout(
            xaxis={"title": "Time"},
            yaxis={"title": "Usage (%)", "range": [0, 100]},
            margin=dict(l=40, r=20, t=20, b=30),  # Add space on the left
        ),
    }


def cpu_layout():
    """
    Create the layout for the CPU usage graph.

    Returns:
        html.Div: HTML division containing the CPU usage graph.
    """
    return html.Div(
        [
            html.H4("CPU Usage", className="graph-title"),
            dcc.Graph(id="cpu-graph", className="graph-content"),
        ]
    )
