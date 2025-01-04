from dash import dcc, html
import plotly.graph_objs as go

def update_disk_graph(disk_data):
    if not disk_data:
        return go.Figure()

    used_gb = disk_data.get("used", 0) / (1024 ** 3)
    free_gb = disk_data.get("free", 0) / (1024 ** 3)
    total_gb = used_gb + free_gb
    used_percentage = (used_gb / total_gb * 100) if total_gb > 0 else 0

    return {
        "data": [
            go.Pie(
                values=[used_gb, free_gb],
                labels=["Used", "Free"],
                hole=.3,
                text=[f"{used_percentage:.1f}%", f"{(100-used_percentage):.1f}%"],
                textinfo="text",
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

def disk_layout():
    return html.Div([
        html.H4("Disk Usage", className="graph-title"),
        dcc.Graph(id="disk-graph", className="graph-content")
    ])