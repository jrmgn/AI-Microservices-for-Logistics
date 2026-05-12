# scripts/train_behavior.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

os.makedirs("models", exist_ok=True)

# --- Example synthetic dataset (replace with real)
rng = np.random.RandomState(0)
n = 1000
X = pd.DataFrame({
    "avg_speed": rng.normal(50, 10, n),
    "harsh_brakes": rng.poisson(2, n),
    "rapid_accel": rng.poisson(1, n),
    "night_driving_pct": rng.uniform(0,1,n),
})

# risk label rule: (toy)
y = ((X["avg_speed"]>65) | (X["harsh_brakes"]>4) | (X["rapid_accel"]>3)).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

clf = RandomForestClassifier(n_estimators=100, random_state=0)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

print(classification_report(y_test, pred))

joblib.dump(clf, "models/driver_behavior_model.joblib")
print("Saved models/driver_behavior_model.joblib")