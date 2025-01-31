# backend/clustering.py
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

def dbscan_clustering(data, eps=0.01, min_samples=2):
    """
    Performs DBSCAN clustering on shipment locations.
    
    Parameters:
        data (pd.DataFrame): DataFrame with 'Latitude' and 'Longitude' columns.
        eps (float): The maximum distance between two samples for one to be considered as in the neighborhood.
        min_samples (int): The minimum number of points required to form a dense region.

    Returns:
        pd.DataFrame: Data with an additional 'cluster' column.
    """
    coordinates = data[['Latitude', 'Longitude']].values
    db = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
    data['cluster'] = db.fit_predict(coordinates)
    return data
