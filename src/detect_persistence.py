import pandas as pd

df = pd.read_csv("data/fires_historical.csv")

print(f"Total historical detections: {len(df)}")
print(f"Date range: {df['acq_date'].min()} to {df['acq_date'].max()}")

# Group nearby points together by rounding coordinates to a grid.
# 0.01 degrees is roughly 1.1km - close enough to treat as "same location"
df["location_group"] = (
    df["latitude"].round(2).astype(str) + "_" + df["longitude"].round(2).astype(str)
)

# For each location, count how many distinct days it showed up as hot
persistence = df.groupby("location_group")["acq_date"].nunique().reset_index()
persistence.columns = ["location_group", "days_detected"]

# Merge counts back into main data, also keep one lat/lon per group for mapping later
location_coords = df.groupby("location_group")[["latitude", "longitude"]].first().reset_index()
persistence = persistence.merge(location_coords, on="location_group")

# Sort so the most persistent locations are at the top
persistence = persistence.sort_values("days_detected", ascending=False)

# Flag locations detected on 10+ distinct days as genuinely "persistent"
# (higher bar than before, since we now have ~130 days of real history)
persistence["is_persistent"] = persistence["days_detected"] >= 10

persistence.to_csv("data/persistent_sources.csv", index=False)

print(f"\nTotal unique locations: {len(persistence)}")
print(f"Persistent locations (10+ distinct days): {persistence['is_persistent'].sum()}")
print("\nTop 10 most persistent locations:")
print(persistence.head(10).to_string(index=False))