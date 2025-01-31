# backend/tsp_solver.py
import numpy as np
import googlemaps

# Constants for vehicle specifications
MAX_3W_CAPACITY = 5
MAX_3W_RADIUS = 15  # km
MAX_4W_EV_CAPACITY = 8
MAX_4W_EV_RADIUS = 20  # km
MAX_4W_RADIUS = float('inf')  # 4W can travel any distance
SOURCE_COORDINATES = (19.075887, 72.877911)  # Lat, Long of source

def get_distance_and_duration(gmaps, origin, destination):
    """
    Fetches the distance and duration between two points using Google Maps API.

    Parameters:
        gmaps (googlemaps.Client): Google Maps API client.
        origin (tuple): (Latitude, Longitude) of the starting point.
        destination (tuple): (Latitude, Longitude) of the ending point.

    Returns:
        tuple: Distance in meters, Duration in seconds.
    """
    result = gmaps.distance_matrix([origin], [destination], mode="driving")
    try:
        distance = result['rows'][0]['elements'][0]['distance']['value']  # in meters
        duration = result['rows'][0]['elements'][0]['duration']['value']  # in seconds
        return distance, duration
    except KeyError:
        return None, None

def tsp_within_cluster_nearest_neighbor(gmaps, locations, vehicle_type):
    """
    Solves the TSP within a cluster using the Nearest Neighbor Heuristic.

    Parameters:
        gmaps (googlemaps.Client): Google Maps API client.
        locations (list): List of (Latitude, Longitude) delivery points.
        vehicle_type (str): Type of vehicle ('3W', '4W-EV', '4W').

    Returns:
        tuple: (Optimized route, Total distance in meters, Total time in seconds).
    """
    # Set max radius based on vehicle type
    max_radius = {
        '3W': MAX_3W_RADIUS,
        '4W-EV': MAX_4W_EV_RADIUS,
        '4W': MAX_4W_RADIUS
    }.get(vehicle_type, MAX_4W_RADIUS)

    total_distance = 0
    total_time = 0
    visited = [False] * len(locations)
    current_location = SOURCE_COORDINATES
    route = [current_location]

    while len(route) < len(locations) + 1:
        nearest_distance = float('inf')
        nearest_location = None
        nearest_index = None

        for i, loc in enumerate(locations):
            if not visited[i]:
                distance, duration = get_distance_and_duration(gmaps, current_location, loc)
                if distance and distance < nearest_distance:
                    nearest_distance = distance
                    nearest_location = loc
                    nearest_index = i
                    total_time += duration  # Add travel time

        if nearest_location:
            visited[nearest_index] = True
            route.append(nearest_location)
            total_distance += nearest_distance
            current_location = nearest_location

    # Add the return trip to the source
    distance, duration = get_distance_and_duration(gmaps, current_location, SOURCE_COORDINATES)
    total_distance += distance
    total_time += duration

    # Check if distance exceeds max radius for the current vehicle
    if total_distance / 1000 > max_radius:  # Convert meters to km
        if vehicle_type == '3W':
            return tsp_within_cluster_nearest_neighbor(gmaps, locations, '4W-EV')
        elif vehicle_type == '4W-EV':
            return tsp_within_cluster_nearest_neighbor(gmaps, locations, '4W')

    route.append(SOURCE_COORDINATES)  # Ensure return to source
    return route, total_distance, total_time
