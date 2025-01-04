import plotly.graph_objs as go
from dash import dcc, html
from services.api_service import fetch_ram_data
from datetime import datetime

def update_ram_graph(ram_data):
    if not ram_data:
        return go.Figure()
    
    labels = ["Used", "Available"]
    values = [ram_data.get("used", 0), ram_data.get("available", 0)]
    return {
        "data": [
            go.Pie(
                labels=labels, 
                values=values,
                hole=.3,
                marker=dict(colors=["#636EFA", "#EF553B"])
            )
        ],
        "layout": go.Layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(l=20, r=20, t=20, b=30),
            height=300
        )
    }



def update_historical_ram_graph(historical_ram_data):
    if not historical_ram_data:
        return go.Figure()
    x_data = [datetime.fromtimestamp(data_point["timestamp"]) for data_point in historical_ram_data]
    y_data = [data_point["total_usage"] for data_point in historical_ram_data]
    return {
        "data": [
            go.Scatter(x=x_data, y=y_data, mode="lines+markers", name="Historical RAM Usage")
        ],
        "layout": go.Layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(l=20, r=20, t=20, b=30),
            height=300,
            xaxis={"title": "Time"},
            yaxis={"title": "Usage (%)", "range": [0, 100]},
        )
    }
    
def ram_layout():
    return html.Div([
        html.H4("RAM Usage", className="graph-title"),
        dcc.Graph(id="ram-graph", className="graph-content")
    ])
