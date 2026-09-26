import pandas as pd
import osmnx as ox
import time
from shapely.geometry import Point

# Set a timeout so slow Overpass queries don't hang forever
ox.settings.timeout = 30

df = pd.read_csv("data/fires_raw.csv")

industrial_tags = {
    "landuse": ["industrial"],
    "building": ["industrial", "warehouse", "factory"],
    "power": ["plant", "substation"],
    "man_made": ["works", "chimney"]
}

def classify_point(lat, lon, radius_m=1000):
    try:
        features = ox.features_from_point((lat, lon), tags=industrial_tags, dist=radius_m)
        if len(features) > 0:
            return "Industrial"
    except Exception as e:
        print(f"    (query issue: {e})")
    return "Other (Vegetation/Agricultural)"

print(f"Classifying {len(df)} fire points...")

classifications = []
for i, row in df.iterrows():
    start = time.time()
    label = classify_point(row["latitude"], row["longitude"])
    elapsed = time.time() - start
    classifications.append(label)
    print(f"  [{i+1}/{len(df)}] ({row['latitude']}, {row['longitude']}) -> {label} ({elapsed:.1f}s)")

df["fire_type"] = classifications
df.to_csv("data/fires_classified.csv", index=False)
print("Saved classified data to data/fires_classified.csv")
print(df["fire_type"].value_counts())