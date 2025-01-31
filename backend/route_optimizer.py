import pandas as pd
import numpy as np
import googlemaps
from sklearn.cluster import DBSCAN

# Constants for vehicle specifications
MAX_3W_CAPACITY = 5
MAX_3W_RADIUS = 15  # km
MAX_4W_EV_CAPACITY = 8
MAX_4W_EV_RADIUS = 20  # km
MAX_4W_RADIUS = float('inf')  # 4W can travel any distance
SOURCE_COORDINATES = (19.1331, 72.9151)  # Latitude and Longitude of the source

# Function to calculate distance and duration using Google Maps API
def get_distance_and_duration(gmaps, origins, destinations):
    try:
        result = gmaps.distance_matrix(origins, destinations, mode="driving")
        distance = np.array([r['elements'][0].get('distance', {}).get('value', None) for r in result['rows']])
        duration = np.array([r['elements'][0].get('duration', {}).get('value', None) for r in result['rows']])
        
        if any(d is None for d in distance) or any(d is None for d in duration):
            return None, None
        return distance, duration
    except Exception as e:
        print(f"Error in distance calculation: {e}")
        return None, None

# DBSCAN Clustering
def dbscan_clustering(data, eps=0.01, min_samples=2):
    coordinates = data[['Latitude', 'Longitude']].values
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
    data['cluster'] = db.fit_predict(coordinates)
    return data

# Nearest Neighbor Heuristic for TSP with dynamic vehicle switching
def tsp_within_cluster_nearest_neighbor(gmaps, locations, vehicle_type):
    max_radius = None

    if vehicle_type == '3W':
        max_radius = MAX_3W_RADIUS
    elif vehicle_type == '4W-EV':
        max_radius = MAX_4W_EV_RADIUS
    elif vehicle_type == '4W':
        max_radius = MAX_4W_RADIUS

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
                distance, duration = get_distance_and_duration(gmaps, [current_location], [loc])
                if distance is not None and distance[0] < nearest_distance:
                    nearest_distance = distance[0]
                    nearest_location = loc
                    nearest_index = i
                    total_time += duration[0] if duration is not None else 0

        if nearest_location:
            visited[nearest_index] = True
            route.append(nearest_location)
            total_distance += nearest_distance
            current_location = nearest_location

    distance, duration = get_distance_and_duration(gmaps, [current_location], [SOURCE_COORDINATES])
    if distance is not None:
        total_distance += distance[0]
        total_time += duration[0] if duration is not None else 0

    if total_distance / 1000 <= max_radius:
        route.append(SOURCE_COORDINATES)
        return route, total_distance, total_time
    elif vehicle_type == '3W':
        return tsp_within_cluster_nearest_neighbor(gmaps, locations, '4W-EV')
    elif vehicle_type == '4W-EV':
        return tsp_within_cluster_nearest_neighbor(gmaps, locations, '4W')

    return None, None, None

# Calculate capacity utilization
def calculate_capacity_utilization(total_shipments, vehicle_type):
    if vehicle_type == '3W':
        return total_shipments / MAX_3W_CAPACITY
    elif vehicle_type == '4W-EV':
        return total_shipments / MAX_4W_EV_CAPACITY
    elif vehicle_type == '4W':
        return 1.0  # No limit for 4W
    return None

# Main function to optimize delivery routes
def measure_clustered_runtime(gmaps, data, eps=0.01, min_samples=2):
    data = dbscan_clustering(data, eps, min_samples)
    optimized_routes = {}

    for cluster_id in np.unique(data['cluster']):
        if cluster_id == -1:  # Skip noise points
            continue
        cluster_data = data[data['cluster'] == cluster_id]
        locations = [(row['Latitude'], row['Longitude']) for _, row in cluster_data.iterrows()]
        total_shipments = len(locations)

        if locations:
            if total_shipments <= MAX_3W_CAPACITY:
                vehicle_type = '3W'
            elif MAX_3W_CAPACITY < total_shipments <= MAX_4W_EV_CAPACITY:
                vehicle_type = '4W-EV'
            else:
                vehicle_type = '4W'

            route, total_distance, total_time = tsp_within_cluster_nearest_neighbor(gmaps, locations, vehicle_type)
            capacity_utilization = calculate_capacity_utilization(total_shipments, vehicle_type)

            optimized_routes[cluster_id] = {
                'route': route,
                'distance': total_distance,
                'time': total_time,
                'vehicle_type': vehicle_type,
                'capacity_utilization': capacity_utilization,
                'shipments': total_shipments
            }
    return optimized_routes

# Save results to a CSV file in the required format
def save_routes_to_csv(clustered_routes, output_file="optimized_routes.csv"):
    results = []
    for cluster_id, details in clustered_routes.items():
        route_str = ' -> '.join([f"({lat:.5f}, {lon:.5f})" for lat, lon in details['route']]) if details['route'] else ''
        results.append({
            'trip_id': f"cluster_{cluster_id}",
            'latitude': details['route'][0][0] if details['route'] else None,
            'longitude': details['route'][0][1] if details['route'] else None,
            'timeslot': None,
            'shipments': details['shipments'],
            'mst_distance': details['distance'] / 1000 if details['distance'] else None,
            'total_time': details['time'] / 60 if details['time'] else None,
            'vehicle_type': details['vehicle_type'],
            'capacity_uti': details['capacity_utilization'],
            'time_uti': None,
            'con_uti': 1,
            'full_route': route_str
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    print(f"Optimized routes saved to {output_file}")
