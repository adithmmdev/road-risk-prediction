import os
import osmnx as ox
import geopandas as gpd

# ======================================================
# OUTPUT PATH
# ======================================================

OUTPUT_PATH = os.path.join("data", "processed", "chennai_cleaned.geojson")

# ======================================================
# DOWNLOAD ROAD NETWORK
# ======================================================

print("Downloading Chennai road network from OSM...")

place_name = "Chennai, Tamil Nadu, India"

G = ox.graph_from_place(
    place_name,
    network_type="drive"
)

# Convert to GeoDataFrame (edges = roads)
gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)

print("Downloaded roads:", gdf.shape)

# ======================================================
# CLEAN DATA
# ======================================================

print("Cleaning road data...")

# Keep only required columns
columns_to_keep = ["geometry", "highway"]
gdf = gdf[columns_to_keep]

# Drop null geometries
gdf = gdf[gdf.geometry.notnull()]

# Reset index
gdf = gdf.reset_index(drop=True)

# ======================================================
# SAVE
# ======================================================

os.makedirs(os.path.join("data", "processed"), exist_ok=True)

gdf.to_file(OUTPUT_PATH, driver="GeoJSON")

print("Saved Chennai roads at:", OUTPUT_PATH)
print("Final shape:", gdf.shape)