AI Microservices for Logistics

This project provides two microservices:
1. Driver Behavior Analysis: A Random Forest classifier to detect risky driving.
2. Route Optimization: A TSP/VRP solver using Google OR-Tools and OSRM data.

Setup:
1. Install dependencies: `pip install -r requirements.txt`
2. Train the model: `python scripts/train_behavior.py`
3. Run the API: `python -m uvicorn app.main:app --reload`


Testing:

Run the automated test suite:
`python -m pytest tests/test_behavior_api.py`


API Authentication:

All endpoints require the following header:
`x-api-key: your-secret-token`
