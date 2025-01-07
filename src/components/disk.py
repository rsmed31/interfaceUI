from dash import dcc, html
import plotly.graph_objs as go


def update_disk_graph(disk_data):
    if not disk_data:
        return go.Figure()

    used_gb = disk_data.get("used", 0) / (1024**3)
    total_gb = (disk_data.get("used", 0) + disk_data.get("free", 0)) / (1024**3)
    percentage_used = (used_gb / total_gb) * 100 if total_gb > 0 else 0

    return {
        "data": [
            go.Indicator(
                mode="gauge+number+delta",
                value=used_gb,
                title={"text": "Disk Usage (GB)"},
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
        "layout": go.Layout(margin=dict(l=20, r=20, t=20, b=30), height=300),
    }


def disk_layout():
    return html.Div(
        [
            html.H4("Disk Usage", className="graph-title"),
            dcc.Graph(id="disk-graph", className="graph-content"),
        ]
    )
