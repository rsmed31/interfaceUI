from dash import html

def log_layout(log_data):
    if not log_data:
        return html.Div("No log data available", style={"color": "red"})

    failed = log_data.get("failed", 0)
    succeed = log_data.get("succeed", 0)
    nbwebsites = log_data.get("nbwebsites", {})
    most_viewed_page = max(nbwebsites, key=nbwebsites.get, default="N/A")
    visits_per_page = [html.P(f"{page}: {visits} visits") for page, visits in nbwebsites.items()]

    return html.Div([
        html.H4("Log Data", style={"color": "blue", "marginBottom": "15px"}),
        html.Div([
            html.P(f"Errors: {failed}", style={"color": "red", "marginRight": "15px"}),
            html.P(f"Successes: {succeed}", style={"color": "green", "marginRight": "15px"}),
            html.P(f"Most Viewed Page: {most_viewed_page}", style={"color": "blue"})
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "padding": "10px 20px",
            "margin": "0 auto",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "backgroundColor": "#fff",
            "width": "fit-content",
            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
        }),
        html.Div([
            html.H5("Visits per Page:", style={"color": "black", "marginTop": "20px"}),
            html.Div(visits_per_page, style={
                "color": "black",
                "textAlign": "left"
            })
        ], style={
            "padding": "10px 20px",
            "margin": "20px auto 0 auto",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "backgroundColor": "#fff",
            "width": "fit-content",
            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
        })
    ], style={
        "textAlign": "center",
        "margin": "20px auto"
    })

def aggregated_log_layout(aggregated_data):
    return html.Div([
        html.H4("Log Data for all servers", style={"color": "blue", "marginBottom": "15px"}),
        html.Div([
            html.P(f"Errors: {aggregated_data['failed']}", style={"color": "red", "marginRight": "15px"}),
            html.P(f"Successes: {aggregated_data['succeed']}", style={"color": "green", "marginRight": "15px"}),
            html.P(f"Total Visitors: {aggregated_data['total_visitors']}", style={"color": "blue"})
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "padding": "10px 20px",
            "margin": "0 auto",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "backgroundColor": "#fff",
            "width": "fit-content",
            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
        })
    ], style={
        "textAlign": "center",
        "margin": "20px auto"
    })