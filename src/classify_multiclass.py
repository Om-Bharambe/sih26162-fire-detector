import pandas as pd
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import time
import os

ox.settings.overpass_url = "https://overpass.kumi.systems/api/interpreter"
ox.settings.timeout = 180
ox.settings.log_console = True

# Separate tag groups for each fire type signal
tag_groups = {
    "industrial": {
        "landuse": ["industrial"],
        "building": ["industrial", "warehouse", "factory"],
        "power": ["plant", "substation"],
        "man_made": ["works", "chimney"]
    },
    "mining": {
        "landuse": ["quarry"],
        "man_made": ["mineshaft"]
    },
    "agricultural": {
        "landuse": ["farmland", "meadow", "orchard"]
    },
    "forest": {
        "landuse": ["forest"],
        "natural": ["wood"]
    }
}

df = pd.read_csv("data/fires_raw.csv")

SUBSET_SIZE = 15
df_subset = df.head(SUBSET_SIZE).copy()

# Load persistence info if available, to help identify gas flares
persistence_lookup = {}
if os.path.exists("data/persistent_sources.csv"):
    pdf = pd.read_csv("data/persistent_sources.csv")
    for _, prow in pdf.iterrows():
        persistence_lookup[prow["location_group"]] = prow["days_detected"]

def check_nearby(lat, lon, tags, radius=500):
    try:
        feats = ox.features_from_point((lat, lon), tags=tags, dist=radius)
        return len(feats) > 0
    except Exception:
        return False

results = []
print(f"Classifying {len(df_subset)} points into 5 fire-type categories...")

for i, row in df_subset.iterrows():
    lat, lon = row["latitude"], row["longitude"]
    location_group = f"{round(lat,2)}_{round(lon,2)}"
    days_detected = persistence_lookup.get(location_group, 1)

    is_industrial = check_nearby(lat, lon, tag_groups["industrial"])
    is_mining = check_nearby(lat, lon, tag_groups["mining"])
    is_agri = check_nearby(lat, lon, tag_groups["agricultural"])
    is_forest = check_nearby(lat, lon, tag_groups["forest"])

    # Priority order matters: check most specific/dangerous signals first
    if is_industrial and days_detected >= 10 and row["frp"] > 5:
        fire_type = "Gas Flare"
    elif is_industrial:
        fire_type = "Industrial"
    elif is_mining:
        fire_type = "Mining"
    elif is_agri:
        fire_type = "Agricultural Burning"
    elif is_forest:
        fire_type = "Wildfire"
    else:
        fire_type = "Unclassified"

    print(f"  [{i+1}/{len(df_subset)}] ({lat}, {lon}) -> {fire_type} (days_detected={days_detected})")

    row_result = row.to_dict()
    row_result["fire_type"] = fire_type
    row_result["days_detected"] = days_detected
    results.append(row_result)

    pd.DataFrame(results).to_csv("data/fires_classified.csv", index=False)
    time.sleep(1)

print("\nDone. Final breakdown:")
print(pd.DataFrame(results)["fire_type"].value_counts())