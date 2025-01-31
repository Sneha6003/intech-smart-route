# backend/vehicle_assignment.py

# Vehicle capacity constraints
MAX_3W_CAPACITY = 5
MAX_4W_EV_CAPACITY = 8

def assign_vehicle_type(num_stations):
    """
    Assigns the appropriate vehicle type based on the number of delivery locations in a cluster.

    Parameters:
        num_stations (int): Number of delivery points in the cluster.

    Returns:
        str: Vehicle type ('3W', '4W-EV', or '4W').
    """
    if num_stations < MAX_3W_CAPACITY:
        return '3W'  # Three-wheeler for smaller deliveries
    elif num_stations <= MAX_4W_EV_CAPACITY:
        return '4W-EV'  # Four-wheeler Electric Vehicle for mid-range deliveries
    else:
        return '4W'  # Regular Four-wheeler for larger deliveries
