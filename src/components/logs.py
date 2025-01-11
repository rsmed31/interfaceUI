from dash import html


def log_layout(log_data):
    if not log_data:
        return html.Div("No log data available", style={"color": "red"})

    failed = log_data.get("failed", 0)
    succeed = log_data.get("succeed", 0)
    nbwebsites = log_data.get("nbwebsites", {})
    most_viewed_page = max(nbwebsites, key=nbwebsites.get, default="N/A")
    visits_per_page = [
        html.P(f"{page}: {visits} visits") for page, visits in nbwebsites.items()
    ]

    return html.Div(
        [
            html.H4("Log Data", style={"color": "blue", "marginBottom": "15px"}),
            html.Div(
                [
                    html.P(f"Errors: {failed}", style={"color": "red"}),
                    html.P(f"Successes: {succeed}", style={"color": "green"}),
                    html.P(
                        f"Most Viewed Page: {most_viewed_page}", style={"color": "blue"}
                    ),
                ],
                className="log-data-container",
            ),
            html.Div(
                [
                    html.H5(
                        "Visits per Page:",
                        style={"color": "black", "marginTop": "20px"},
                    ),
                    html.Div(visits_per_page, className="log-container"),
                ],
                className="log-container",
            ),
        ],
        className="log-container",
    )


def aggregated_log_layout(aggregated_data):
    return html.Div(
        [
            html.H4(
                "Log Data for all servers",
                style={"color": "blue", "marginBottom": "15px"},
            ),
            html.Div(
                [
                    html.P(
                        f"Errors: {aggregated_data['failed']}",
                        style={"color": "red", "marginRight": "15px"},
                    ),
                    html.P(
                        f"Successes: {aggregated_data['succeed']}",
                        style={"color": "green", "marginRight": "15px"},
                    ),
                    html.P(
                        f"Total Visitors: {aggregated_data['total_visitors']}",
                        style={"color": "blue"},
                    ),
                ],
                className="log-data-container",
            ),
        ],
        className="log-container",
    )


def recent_logs_layout(recent_logs):
    if not recent_logs:
        return html.Div("No recent logs available", style={"color": "red"})

    log_items = []
    for log in recent_logs:
        color = "green" if log["status"] == "200" else "red"
        log_items.append(
            html.Div(
                [
                    html.P(f"IP: {log['ip']}", style={"margin": "0"}),
                    html.P(f"Time: {log['time']}", style={"margin": "0"}),
                    html.P(f"Method: {log['request_method']}", style={"margin": "0"}),
                    html.P(f"URL: {log['request_url']}", style={"margin": "0"}),
                    html.P(
                        f"Status: {log['status']}",
                        style={"margin": "0", "color": color},
                    ),
                ],
                style={
                    "border": f"1px solid {color}",
                    "borderRadius": "5px",
                    "padding": "10px",
                    "marginBottom": "10px",
                    "backgroundColor": "#f9f9f9",
                },
            )
        )

    return html.Div(log_items, style={"marginTop": "20px"})
