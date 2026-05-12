import requests
from optim_helpers import solve_vrp

def get_osrm_matrix(coords):
    s = ";".join([f"{lon},{lat}" for lon,lat in coords])
    url = f"http://router.project-osrm.org/table/v1/driving/{s}?annotations=duration"
    print(f"Requesting OSRM data for {len(coords)} locations...")
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError("OSRM request failed")
    return resp.json()["durations"]

locations = [
    [120.9842, 14.5995], # Depot (Manila)
    [121.0361, 14.6133], # Point 1 (San Juan)
    [121.0503, 14.5492], # Point 2 (BGC)
    [121.0014, 14.5176]  # Point 3 (Parañaque)
]

demands = [0, 2, 3, 2] 

vehicle_capacities = [4, 4]

try:
    matrix = get_osrm_matrix(locations)
    
    routes = solve_vrp(matrix, demands, vehicle_capacities)
    
    print("\n--- Validation Results ---")
    for i, route in enumerate(routes):
        print(f"Vehicle {i+1} Route: {route}")
        
except Exception as e:
    print(f"Validation failed: {e}")