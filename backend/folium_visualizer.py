# backend/folium_visualizer.py
import folium

def generate_route_map(route, filename="route_map.html"):
    """
    Generates an interactive map using Folium with the given optimized route.

    Parameters:
        route (list): List of (Latitude, Longitude) tuples representing the optimized route.
        filename (str): Name of the output HTML file to save the map.

    Returns:
        str: Path to the saved HTML file.
    """
    if not route:
        return None

    # Create a map centered around the first location
    route_map = folium.Map(location=route[0], zoom_start=12)

    # Add markers for each location
    for i, point in enumerate(route):
        folium.Marker(
            location=point,
            popup=f"Stop {i+1}",
            icon=folium.Icon(color="blue" if i == 0 else "green"),
        ).add_to(route_map)

    # Add a polyline to connect all points in order
    folium.PolyLine(route, color="red", weight=2.5, opacity=0.8).add_to(route_map)

    # Save the map to an HTML file
    route_map.save(filename)
    return filename
