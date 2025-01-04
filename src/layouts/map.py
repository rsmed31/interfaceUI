import dash_leaflet as dl
from dash import html

def map_layout(ip_locations):
    # Filter out None values
    valid_locations = {ip: loc for ip, loc in ip_locations.items() if loc is not None}
    
    if not valid_locations:
        return html.Div([
            html.H4("IP Location Map", className="text-center mb-20"),
            html.P("No public IP addresses available for geolocation", 
                  className="text-center")
        ], className="card")
    
    # Calculate center point
    valid_coords = [(loc["latitude"], loc["longitude"]) 
                   for loc in valid_locations.values()]
    
    if not valid_coords:
        return html.Div("No valid locations found", className="text-center")
    
    center_lat = sum(lat for lat, _ in valid_coords) / len(valid_coords)
    center_lon = sum(lon for _, lon in valid_coords) / len(valid_coords)
    
    markers = [
        dl.Marker(position=[loc["latitude"], loc["longitude"]], 
                 children=[dl.Tooltip(f"IP: {ip}")]) 
        for ip, loc in valid_locations.items()
    ]

    return html.Div([
        html.H4("IP Location Map", className="text-center mb-20"),
        html.Div([
            dl.Map([
                dl.TileLayer(url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
                dl.LayerGroup(markers)
            ], 
            center=[center_lat, center_lon], 
            zoom=2,
            className="leaflet-container")
        ], className="map-container"),
        html.Div(
            f"Displaying {len(markers)} locations", 
            className="text-center mt-20"
        )
    ], className="card")