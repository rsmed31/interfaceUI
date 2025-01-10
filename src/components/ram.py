import plotly.graph_objs as go
from dash import dcc, html
from services.api_service import fetch_data
from datetime import datetime

def update_ram_graph(ram_data):
    if not ram_data:
        return go.Figure()

    # Convert bytes to gigabytes
    used_gb = ram_data.get("used", 0) / (1024**3)
    total_gb = (ram_data.get("used", 0) + ram_data.get("available", 0)) / (1024**3)
    percentage_used = (used_gb / total_gb) * 100 if total_gb > 0 else 0

    return {
        "data": [
            go.Indicator(
                mode="gauge+number+delta",
                value=used_gb,
                title={"text": "RAM Usage (GB)"},
                delta={"reference": total_gb},
                gauge={
                    "axis": {"range": [0, total_gb]},
                    "bar": {"color": "#EF553B"},
                    "steps": [
                        {"range": [0, total_gb * 0.5], "color": "#636EFA"},
                        {"range": [total_gb * 0.5, total_gb], "color": "#EF553B"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": used_gb,
                    },
                },
            )
        ],
        "layout": go.Layout(margin=dict(l=40, r=20, t=20, b=30), height=300),  # Add space on the left
    }

def update_historical_ram_graph(historical_ram_data):
    if not historical_ram_data:
        return go.Figure()
        
    x_data = [datetime.fromtimestamp(point[0]) for point in historical_ram_data]
    y_data = [point[1] for point in historical_ram_data]
    
    return {
        "data": [
            go.Scatter(x=x_data, y=y_data, mode="lines+markers", name="Historical RAM Usage")
        ],
        "layout": go.Layout(
            xaxis={"title": "Time"},
            yaxis={"title": "Usage (%)", "range": [0, 100]},
            margin=dict(l=40, r=20, t=20, b=30),  # Add space on the left
        )
    }
    
def ram_layout():
    return html.Div(
        [
            html.H4("RAM Usage", className="graph-title"),
            dcc.Graph(id="ram-graph", className="graph-content"),
        ]
    )