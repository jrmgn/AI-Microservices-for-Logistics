# tests/test_behavior_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_behavior():
    # Note: We add the header here because we just enabled Auth
    resp = client.post(
        "/predict_behavior", 
        json={"avg_speed": 70, "harsh_brakes": 3, "rapid_accel": 1, "night_driving_pct": 0.1},
        headers={"x-api-key": "your-secret-token"}
    )
    assert resp.status_code == 200
    j = resp.json()
    assert "risk_label" in j

def test_optimize_route():
    resp = client.post(
        "/optimize_route",
        json={
            "locations": [
                {"id":"0","lon":120.98,"lat":14.6},
                {"id":"1","lon":121.00,"lat":14.61},
                {"id":"2","lon":121.01,"lat":14.62}
            ],
            "use_osrm": True
        },
        headers={"x-api-key": "your-secret-token"}
    )
    assert resp.status_code == 200
    j = resp.json()
    assert "route" in j
    assert len(j["route"]) > 0