import pandas as pd
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import time

ox.settings.overpass_url = "https://overpass.kumi.systems/api/interpreter"
ox.settings.timeout = 180
ox.settings.log_console = True

industrial_tags = {
    "landuse": ["industrial"],
    "building": ["industrial", "warehouse", "factory"],
    "power": ["plant", "substation"],
    "man_made": ["works", "chimney"]
}

df = pd.read_csv("data/fires_raw.csv")

SUBSET_SIZE = 15
df_subset = df.head(SUBSET_SIZE).copy()

results = []

print(f"Computing distance-to-industrial for {len(df_subset)} fire points...")

for i, row in df_subset.iterrows():
    min_distance_m = 5000  # default: "far away" if nothing found within search radius
    try:
        feats = ox.features_from_point(
            (row["latitude"], row["longitude"]),
            tags=industrial_tags,
            dist=2000  # search up to 2km, wider than before, so we can measure real distance
        )
        if len(feats) > 0:
            fire_point = gpd.GeoSeries([Point(row["longitude"], row["latitude"])], crs="EPSG:4326")
            feats_proj = feats.to_crs("EPSG:32643")
            fire_proj = fire_point.to_crs("EPSG:32643")
            distances = feats_proj.geometry.distance(fire_proj.iloc[0])
            min_distance_m = distances.min()
        print(f"  [{i+1}/{len(df_subset)}] nearest industrial feature: {min_distance_m:.0f}m")
    except Exception as e:
        print(f"  [{i+1}/{len(df_subset)}] query failed, defaulting to far: {e}")

    row_result = row.to_dict()
    row_result["dist_to_industrial_m"] = min_distance_m
    results.append(row_result)

    pd.DataFrame(results).to_csv("data/fires_with_distance.csv", index=False)
    time.sleep(1)

print(f"Done. Saved {len(results)} points with distance to data/fires_with_distance.csv")