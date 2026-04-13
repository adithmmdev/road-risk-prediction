import joblib
import pandas as pd
import numpy as np
import os

# ======================================================
# PATHS
# ======================================================

ML_MODEL_PATH = os.path.join("models", "universal_severity_model.pkl")
ML_FEATURE_PATH = os.path.join("models", "universal_feature_names.pkl")
ML_SCALER_PATH = os.path.join("models", "universal_target_bounds.pkl")

GEOMETRY_PATH = os.path.join("data", "processed", "chennai_geometry_final.csv")

# ======================================================
# LOAD ARTIFACTS
# ======================================================

print("Loading ML model...")
model = joblib.load(ML_MODEL_PATH)

print("Loading feature names...")
feature_names = joblib.load(ML_FEATURE_PATH)

print("Loading normalization bounds...")
min_target, max_target = joblib.load(ML_SCALER_PATH)

print("Loading geometry data...")
geo_df = pd.read_csv(GEOMETRY_PATH)

# ======================================================
# SIMULATED FRONTEND INPUT
# ======================================================

request = {
    "road_index": 4,
    "visibility": 1,         # LOW visibility → dangerous
    "temperature": 95,
    "humidity": 90,
    "weather": "Rain",
    "hour": 23,
    "is_weekend": 1
}

segment = geo_df.iloc[request["road_index"]]

# ======================================================
# BUILD ML INPUT
# ======================================================

ml_input = {col: 0 for col in feature_names}

# Environmental
ml_input["Visibility(mi)"] = request["visibility"]
ml_input["Temperature(F)"] = request["temperature"]
ml_input["Humidity(%)"] = request["humidity"]

# Temporal
ml_input["Hour"] = request["hour"]
ml_input["is_night"] = 1 if request["hour"] >= 18 or request["hour"] < 6 else 0
ml_input["is_weekend"] = request["is_weekend"]

# Structural (from geometry)
ml_input["Junction"] = 0
ml_input["Traffic_Signal"] = 0
ml_input["Roundabout"] = 0
ml_input["Railway"] = 0
ml_input["Bump"] = 0

# Weather encoding (IMPORTANT FIX)
weather_map = {
    "Rain": "Weather_Simplified_Rain",
    "Fog": "Weather_Simplified_Fog",
    "Snow": "Weather_Simplified_Snow",
    "Storm": "Weather_Simplified_Storm"
}

if request["weather"] in weather_map:
    col = weather_map[request["weather"]]
    if col in ml_input:
        ml_input[col] = 1

# Convert to DataFrame
X = pd.DataFrame([ml_input])[feature_names]

# ======================================================
# ML PREDICTION
# ======================================================

print("\nPredicting ML risk...")

raw = model.predict(X)[0]

ml_norm = (raw - min_target) / (max_target - min_target)
ml_norm = np.clip(ml_norm, 0, 1)
ml_risk = round(float(ml_norm * 100), 2)

# ======================================================
# GEOMETRY RISK
# ======================================================

geometry_risk = float(segment["geometry_risk_score"])
if geometry_risk ==0:
    print("Warning: Geometry risk is 0");

# ======================================================
# FUSION
# ======================================================

final_risk = round(0.65 * ml_risk + 0.35 * geometry_risk, 2)

# ======================================================
# RISK CATEGORY
# ======================================================

if final_risk < 35:
    tier = "LOW"
elif final_risk < 70:
    tier = "MEDIUM"
else:
    tier = "HIGH"

# ======================================================
# OUTPUT
# ======================================================

print("\n--- FINAL RESULT ---")
print({
    "ml_risk": ml_risk,
    "geometry_risk": geometry_risk,
    "final_risk": final_risk,
    "risk_tier": tier
})