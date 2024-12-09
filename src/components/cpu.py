import plotly.graph_objs as go
from dash import dcc, html
from services.api_service import fetch_cpu_data

def update_cpu_graph(cpu_data):
    if not cpu_data:
        return go.Figure()
    x_data = [f"Core {core['id']}" for core in cpu_data]
    y_data = [float(core["usage"]) for core in cpu_data]
    return {
        "data": [
            go.Scatter(x=x_data, y=y_data, mode="lines+markers", name="CPU Usage")
        ],
        "layout": go.Layout(
            title="CPU Usage",
            xaxis={"title": "Cores"},
            yaxis={"title": "Usage (%)", "range": [0, 100]},
        )
    }

def cpu_layout():
    return html.Div([
        html.H4("CPU Usage", style={"textAlign": "center", "color": "blue"}),
        dcc.Graph(id="cpu-graph")
    ])
