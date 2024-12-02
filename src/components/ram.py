import plotly.graph_objs as go
from dash import dcc, html
from services.api_service import fetch_ram_data

def update_ram_graph():
    data = fetch_ram_data()
    if not data:
        return go.Figure()  # Return empty figure when no data is available
    labels = ["Used", "Available"]
    values = [data["used"], data["available"]]
    return {
        "data": [go.Pie(labels=labels, values=values)],
        "layout": go.Layout(title="RAM Usage")
    }

def ram_layout():
    return html.Div([
        html.H4("RAM Usage", style={"textAlign": "center", "color": "blue"}),
        dcc.Graph(id="ram-graph")
    ])
