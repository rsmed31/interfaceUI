import plotly.graph_objs as go
from dash import dcc, html
from services.api_service import fetch_ram_data

def update_ram_graph(ram_data):
    if not ram_data:
        return go.Figure()
    labels = ["Used", "Available"]
    values = [ram_data.get("used", 0), ram_data.get("available", 0)]
    return {
        "data": [go.Pie(labels=labels, values=values)],
        "layout": go.Layout(title="RAM Usage"),
    }

def ram_layout():
    return html.Div([
        html.H4("RAM Usage", style={"textAlign": "center", "color": "blue"}),
        dcc.Graph(id="ram-graph")
    ])
