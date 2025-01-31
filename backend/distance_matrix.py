# backend/distance_matrix.py
import googlemaps

def get_distance_and_duration(gmaps, origin, destination):
    """
    Fetches the distance and duration between two points using Google Maps API.

    Parameters:
        gmaps (googlemaps.Client): Google Maps API client.
        origin (tuple): (Latitude, Longitude) of the starting point.
        destination (tuple): (Latitude, Longitude) of the ending point.

    Returns:
        tuple: (Distance in meters, Duration in seconds).
    """
    result = gmaps.distance_matrix([origin], [destination], mode="driving")
    try:
        distance = result['rows'][0]['elements'][0]['distance']['value']  # in meters
        duration = result['rows'][0]['elements'][0]['duration']['value']  # in seconds
        return distance, duration
    except KeyError:
        return None, None
