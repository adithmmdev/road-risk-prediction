import sys
import json
import joblib
import pandas as pd
import numpy as np
import os

# ======================================================
# SAFE BASE DIRECTORY (INDUSTRY LEVEL)
# ======================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# ======================================================
# PATHS
# ======================================================

ML_MODEL_PATH = os.path.join(BASE_DIR, "models", "universal_severity_model.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "models", "universal_feature_names.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "universal_target_bounds.pkl")
GEOMETRY_PATH = os.path.join(BASE_DIR, "data", "processed", "chennai_geometry_final.csv")

# ======================================================
# VALIDATION (VERY IMPORTANT)
# ======================================================

for path in [ML_MODEL_PATH, FEATURE_PATH, SCALER_PATH, GEOMETRY_PATH]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

# ======================================================
# LOAD INPUT
# ======================================================

input_data = json.loads(sys.argv[1])

# ======================================================
# LOAD ARTIFACTS
# ======================================================

model = joblib.load(ML_MODEL_PATH)
feature_names = joblib.load(FEATURE_PATH)
min_target, max_target = joblib.load(SCALER_PATH)
geo_df = pd.read_csv(GEOMETRY_PATH)

# ======================================================
# VALIDATE INDEX
# ======================================================

road_index = input_data["road_index"]

if road_index >= len(geo_df):
    raise ValueError("Invalid road_index")

segment = geo_df.iloc[road_index]

# ======================================================
# BUILD ML INPUT
# ======================================================

ml_input = {col: 0 for col in feature_names}

ml_input["Visibility(mi)"] = input_data["visibility"]
ml_input["Temperature(F)"] = input_data["temperature"]
ml_input["Humidity(%)"] = input_data["humidity"]

ml_input["Hour"] = input_data["hour"]
ml_input["is_night"] = 1 if input_data["hour"] >= 18 or input_data["hour"] < 6 else 0
ml_input["is_weekend"] = input_data["is_weekend"]

ml_input["Junction"] = 0
ml_input["Traffic_Signal"] = 0
ml_input["Roundabout"] = 0
ml_input["Railway"] = 0
ml_input["Bump"] = 0

weather_map = {
    "Rain": "Weather_Simplified_Rain",
    "Fog": "Weather_Simplified_Fog",
    "Snow": "Weather_Simplified_Snow",
    "Storm": "Weather_Simplified_Storm"
}

if input_data["weather"] in weather_map:
    col = weather_map[input_data["weather"]]
    if col in ml_input:
        ml_input[col] = 1

X = pd.DataFrame([ml_input])[feature_names]

# ======================================================
# ML PREDICTION
# ======================================================

raw = model.predict(X)[0]
ml_norm = (raw - min_target) / (max_target - min_target)
ml_risk = float(np.clip(ml_norm, 0, 1) * 100)

# ======================================================
# GEOMETRY
# ======================================================

geometry_risk = float(segment["geometry_risk_score"])

# ======================================================
# FUSION
# ======================================================

final_risk = 0.65 * ml_risk + 0.35 * geometry_risk

# ======================================================
# RISK TIER
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

result = {
    "ml_risk": round(ml_risk, 2),
    "geometry_risk": round(geometry_risk, 2),
    "final_risk": round(final_risk, 2),
    "risk_tier": tier
}

print(json.dumps(result))