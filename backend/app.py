from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import csv
import googlemaps
from route_optimizer import measure_clustered_runtime, save_routes_to_csv

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend communication

# Google Maps API setup
api_key = "AIzaSyB-LxwbA7D-kCu2LB0zZWJwBn5dUWhGen4"
gmaps = googlemaps.Client(key=api_key)

@app.route('/')
def home():
    return "Welcome to the Route Optimizer API! Use /optimize with a POST request and a CSV file."

@app.route('/optimize', methods=['POST'])
def optimize_routes():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "⚠️ No file part in request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "⚠️ No selected file"}), 400

        print(f"✅ Received file: {file.filename}")  # Debugging
        data = pd.read_csv(file)
        print(f"✅ Data received: {data.shape}")  # Debugging

        # Process the file
        eps = 0.01
        min_samples = 2
        clustered_routes = measure_clustered_runtime(gmaps, data, eps, min_samples)
        
        output_file = "optimized_routes.csv"
        save_routes_to_csv(clustered_routes, output_file)

        return jsonify({"message": "Route optimization completed", "output_file": output_file})
    
    except Exception as e:
        print("❌ Backend error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/get_routes', methods=['GET'])
def get_routes():
    try:
        routes = []
        with open("optimized_routes.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                routes.append({
                    "trip_id": row["trip_id"],
                    "shipments": int(row["shipments"]),
                    "mst_distance": float(row["mst_distance"]),
                    "total_time": float(row["total_time"]),
                    "vehicle_type": row["vehicle_type"]
                })
        return jsonify(routes)
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV: {str(e)}"}), 500

# 📥 New Endpoint: Download the optimized CSV file
@app.route('/download', methods=['GET'])
def download_file():
    try:
        return send_file("optimized_routes.csv", as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Failed to download file: {str(e)}"}), 500

if __name__ == '__main__':
    print("🔥 Flask API is running! Open http://127.0.0.1:5000/optimize")
    app.run(debug=True)
