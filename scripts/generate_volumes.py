import os
import pandas as pd
import requests

# Get the URL from GitHub secret
CSV_URL = os.environ.get("CSV_URL")
if not CSV_URL:
    raise RuntimeError("❌ CSV_URL secret not found")

print("📦 Downloading CSV from:", CSV_URL)
r = requests.get(CSV_URL, timeout=60)
r.raise_for_status()
with open("products.csv", "wb") as f:
    f.write(r.content)

# Read and process CSV
df = pd.read_csv("products.csv", encoding="windows-1250", sep=";", decimal=",")

# Make sure expected columns exist
cols = ["name", "height", "depth", "width"]
for c in cols:
    if c not in df.columns:
        print(f"⚠️ Missing column '{c}', creating empty one")
        df[c] = 0

# Replace NaNs with 0
df = df.fillna(0)

# Convert and calculate volume
for c in ["height", "depth", "width"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
df["volume"] = df["height"] * df["depth"] * df["width"]

# Keep only useful columns
result = df[["name", "volume"]].copy()
result.to_json("volumes.json", orient="records", force_ascii=False, indent=2)

print(f"✅ Done — generated volumes.json with {len(result)} items")
