import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load the data with computed distances
df = pd.read_csv("data/fires_with_distance.csv")

# Bootstrap labels: our rule-based ground truth (distance < 500m = Industrial)
df["label"] = (df["dist_to_industrial_m"] < 500).astype(int)  # 1 = Industrial, 0 = Other

# Features the model will learn from
features = ["dist_to_industrial_m", "frp", "bright_ti4", "bright_ti5"]
X = df[features]
y = df["label"]

print(f"Training on {len(df)} points | Industrial: {y.sum()} | Other: {len(y) - y.sum()}")

# With only 15 points, we can't do a meaningful train/test split (too few samples).
# We're being upfront: this trains on all available data, since the goal here is a
# working probability-scoring model for the demo, not a rigorously validated one yet.
model = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
model.fit(X, y)

# Save the trained model so the app can load it later
joblib.dump(model, "data/fire_classifier.pkl")
print("Model saved to data/fire_classifier.pkl")

# Show feature importance so we understand what the model is using
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\nFeature importance:")
print(importances)

# Generate predictions with confidence scores for all points
df["predicted_probability_industrial"] = model.predict_proba(X)[:, 1]
df["fire_type"] = df["predicted_probability_industrial"].apply(lambda p: "Industrial" if p >= 0.5 else "Other (Vegetation/Agricultural)")

df.to_csv("data/fires_classified.csv", index=False)
print("\nSaved predictions with confidence to data/fires_classified.csv")
print(df[["latitude", "longitude", "dist_to_industrial_m", "predicted_probability_industrial", "fire_type"]])