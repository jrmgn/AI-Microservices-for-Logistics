# app/main.py
from fastapi import FastAPI, HTTPException, Header, Depends 
from pydantic import BaseModel
import joblib
import numpy as np
import requests
import os
import json
from scripts.optim_helpers import solve_tsp, solve_vrp
from app.db import init_db, log_inference 

# Initialize DB on startup
init_db()

app = FastAPI(title="DriverBehavior + RouteOpt API")

# Security Token
API_TOKEN = "your-secret-token"

def get_token(x_api_key: str = Header(...)):
    if x_api_key != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return x_api_key

# Load driver model
MODEL_PATH = os.getenv("BEHAVIOR_MODEL_PATH", "models/driver_behavior_model.joblib")
driver_model = joblib.load(MODEL_PATH)

# --- Pydantic Models ---

class BehaviorRequest(BaseModel):
    avg_speed: float
    harsh_brakes: int
    rapid_accel: int
    night_driving_pct: float

class BehaviorResponse(BaseModel):
    risk_prob: float
    risk_label: int

class Location(BaseModel):
    id: str
    lon: float
    lat: float

class RouteRequest(BaseModel):
    locations: list[Location]
    use_osrm: bool = True

class RouteResponse(BaseModel):
    route: list[int]

class VRPRequest(BaseModel):
    locations: list[Location]
    demands: list[int]
    vehicle_capacities: list[int]
    use_osrm: bool = True

class VRPResponse(BaseModel):
    routes: list[list[int]]

# --- Helper Functions ---

def osrm_table(coords):
    s = ";".join([f"{lon},{lat}" for lon,lat in coords])
    url = f"http://router.project-osrm.org/table/v1/driving/{s}?annotations=duration,distance"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError("OSRM table failed")
    j = resp.json()
    if "durations" in j:
        return j["durations"]
    return j["distances"]

# --- Endpoints ---

@app.post("/predict_behavior", response_model=BehaviorResponse)
def predict_behavior(req: BehaviorRequest, token: str = Depends(get_token)):
    log_inference("/predict_behavior", req.model_dump_json())
    
    X = np.array([[req.avg_speed, req.harsh_brakes, req.rapid_accel, req.night_driving_pct]])
    prob = driver_model.predict_proba(X)[0,1] if hasattr(driver_model, "predict_proba") else None
    label = int(driver_model.predict(X)[0])
    return {"risk_prob": float(prob) if prob is not None else None, "risk_label": label}

@app.post("/optimize_route", response_model=RouteResponse)
def optimize_route(req: RouteRequest, token: str = Depends(get_token)):
    log_inference("/optimize_route", req.model_dump_json())
    
    if len(req.locations) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 locations (including depot)")
    
    coords = [(loc.lon, loc.lat) for loc in req.locations]
    if req.use_osrm:
        matrix = osrm_table(coords)
    else:
        n = len(coords)
        matrix = [[0]*n for _ in range(n)]
        import math
        for i in range(n):
            for j in range(n):
                dx = coords[i][0]-coords[j][0]
                dy = coords[i][1]-coords[j][1]
                matrix[i][j] = math.hypot(dx,dy)
    
    route = solve_tsp(matrix)
    if route is None:
        raise HTTPException(status_code=500, detail="Route solver failed")
    return {"route": route}

@app.post("/optimize_vrp", response_model=VRPResponse)
def optimize_vrp(req: VRPRequest, token: str = Depends(get_token)):
    log_inference("/optimize_vrp", req.model_dump_json())
    
    if len(req.locations) != len(req.demands):
        raise HTTPException(status_code=400, detail="Locations and demands must match in length")
    
    coords = [(loc.lon, loc.lat) for loc in req.locations]
    if req.use_osrm:
        matrix = osrm_table(coords)
    else:
        n = len(coords)
        matrix = [[0]*n for _ in range(n)]
        import math
        for i in range(n):
            for j in range(n):
                matrix[i][j] = math.hypot(coords[i][0]-coords[j][0], coords[i][1]-coords[j][1])

    routes = solve_vrp(matrix, req.demands, req.vehicle_capacities)
    if routes is None:
        raise HTTPException(status_code=500, detail="VRP solver failed")
    return {"routes": routes}