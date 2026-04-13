import geopandas as gpd
import pandas as pd
import numpy as np
import os
import joblib
from shapely.geometry import LineString

# ======================================================
# PATHS
# ======================================================

INPUT_GEOJSON = os.path.join("data", "processed", "chennai_cleaned.geojson")
OUTPUT_PATH = os.path.join("data", "processed", "chennai_geometry_final.csv")
SCALER_PATH = os.path.join("models", "geometry_risk_scaler.pkl")

# ======================================================
# LOAD DATA
# ======================================================

print("Loading Chennai road geometries...")
gdf = gpd.read_file(INPUT_GEOJSON)

print("Initial shape:", gdf.shape)

# Convert to metric CRS
print("Projecting CRS...")
gdf = gdf.to_crs(epsg=32644)

# ======================================================
# 1️⃣ ROAD LENGTH
# ======================================================

gdf["road_length_m"] = gdf.geometry.length

# ======================================================
# 2️⃣ CURVATURE (normalized per segment)
# ======================================================

def compute_curvature(line):
    if not isinstance(line, LineString):
        return 0.0

    coords = list(line.coords)
    if len(coords) < 3:
        return 0.0

    total_angle = 0.0

    for i in range(1, len(coords) - 1):
        p1 = np.array(coords[i - 1])
        p2 = np.array(coords[i])
        p3 = np.array(coords[i + 1])

        v1 = p1 - p2
        v2 = p3 - p2

        denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-6
        cos_angle = np.dot(v1, v2) / denom
        angle = np.arccos(np.clip(cos_angle, -1, 1))

        total_angle += angle

    return total_angle / (line.length + 1e-6)

print("Computing curvature...")
gdf["curvature"] = gdf.geometry.apply(compute_curvature)

# ======================================================
# 3️⃣ INTERSECTION DENSITY
# ======================================================

print("Computing intersection density...")

gdf["intersection_density"] = 0
sindex = gdf.sindex

for idx, row in gdf.iterrows():
    buffer = row.geometry.buffer(120)

    possible = list(sindex.intersection(buffer.bounds))
    neighbors = gdf.iloc[possible]

    count = neighbors.intersects(buffer).sum() - 1
    gdf.at[idx, "intersection_density"] = max(count, 0)

# Normalize
gdf["intersection_density"] /= (gdf["intersection_density"].max() + 1e-6)

# ======================================================
# 4️⃣ NETWORK DENSITY
# ======================================================

print("Computing network density...")

gdf["network_density"] = 0

for idx, row in gdf.iterrows():
    buffer = row.geometry.buffer(200)

    possible = list(sindex.intersection(buffer.bounds))
    neighbors = gdf.iloc[possible]

    gdf.at[idx, "network_density"] = len(neighbors)

gdf["network_density"] /= (gdf["network_density"].max() + 1e-6)

# ======================================================
# 5️⃣ ROAD TYPE WEIGHT
# ======================================================

print("Processing road hierarchy...")

if "highway" not in gdf.columns:
    raise ValueError("Missing 'highway' column")

gdf["is_primary"] = gdf["highway"].str.contains("primary", na=False).astype(int)
gdf["is_secondary"] = gdf["highway"].str.contains("secondary", na=False).astype(int)
gdf["is_residential"] = gdf["highway"].str.contains("residential", na=False).astype(int)

gdf["road_weight"] = (
    gdf["is_primary"] * 1.0 +
    gdf["is_secondary"] * 0.7 +
    gdf["is_residential"] * 0.4
).clip(0, 1)

# ======================================================
# NORMALIZATION (CRITICAL FIX)
# ======================================================

print("Normalizing features...")

gdf["length_norm"] = gdf["road_length_m"] / (gdf["road_length_m"].max() + 1e-6)

# Normalize curvature robustly
low_c = gdf["curvature"].quantile(0.05)
high_c = gdf["curvature"].quantile(0.95)

gdf["curvature_norm"] = ((gdf["curvature"] - low_c) / (high_c - low_c)).clip(0, 1)

# ======================================================
# FINAL GEOMETRY SCORE
# ======================================================

print("Computing final geometry risk...")

gdf["geometry_raw"] = (
    0.25 * gdf["length_norm"] +
    0.25 * gdf["curvature_norm"] +
    0.20 * gdf["intersection_density"] +
    0.20 * gdf["network_density"] +
    0.10 * gdf["road_weight"]
)

# ======================================================
# FINAL SCALING (0–100)
# ======================================================

print("Scaling to 0–100...")

low = gdf["geometry_raw"].quantile(0.05)
high = gdf["geometry_raw"].quantile(0.95)

gdf["geometry_scaled"] = ((gdf["geometry_raw"] - low) / (high - low)).clip(0, 1)
gdf["geometry_risk_score"] = (gdf["geometry_scaled"] * 100).round(2)

# Save scaler
os.makedirs("models", exist_ok=True)
joblib.dump((low, high), SCALER_PATH)

# ======================================================
# SAVE
# ======================================================

gdf[[
    "road_length_m",
    "curvature",
    "intersection_density",
    "network_density",
    "road_weight",
    "geometry_risk_score"
]].to_csv(OUTPUT_PATH, index=False)

print("Saved final geometry risk.")
print("\nDistribution:")
print(gdf["geometry_risk_score"].describe())