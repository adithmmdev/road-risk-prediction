import osmnx as ox

place = "Chennai, Tamil Nadu, India"

print("Downloading road network...")

G = ox.graph_from_place(place, network_type="drive")

gdf = ox.graph_to_gdfs(G, nodes=False)

gdf = gdf.reset_index(drop=True)

# Assign stable road_id
gdf["road_id"] = gdf.index

# Keep only needed
gdf = gdf[["road_id", "geometry"]]

gdf.to_file("chennai_roads.geojson", driver="GeoJSON")

print("Saved chennai_roads.geojson")