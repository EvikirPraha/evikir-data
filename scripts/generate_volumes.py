import os
import pandas as pd
import requests
import chardet

# Get the URL from GitHub secret
CSV_URL = os.environ.get("CSV_URL")
if not CSV_URL:
    raise RuntimeError("❌ CSV_URL secret not found")

print("📦 Downloading CSV from:", CSV_URL)
r = requests.get(CSV_URL, timeout=60)
r.raise_for_status()

# Save temporary CSV
with open("products.csv", "wb") as f:
    f.write(r.content)

# Try to detect encoding
with open("products.csv", "rb") as f:
    rawdata = f.read(200000)
detection = chardet.detect(rawdata)
encoding_guess = detection.get("encoding") or "windows-1250"
print("🔍 Detected encoding:", encoding_guess)

# Try reading the CSV safely
encodings_to_try = [encoding_guess, "windows-1250", "windows-1252", "latin-2", "utf-8-sig"]

for enc in encodings_to_try:
    try:
        df = pd.read_csv("products.csv", encoding=enc, sep=";", decimal=",", on_bad_lines="skip")
        print(f"✅ Successfully read CSV with encoding: {enc}")
        break
    except Exception as e:
        print(f"⚠️ Failed with {enc}: {e}")
else:
    raise RuntimeError("❌ Could not read CSV with any encoding")

# Ensure required columns exist
cols = ["name", "height", "depth", "width"]
for c in cols:
    if c not in df.columns:
        print(f"⚠️ Missing column '{c}', creating empty one")
        df[c] = 0

# Clean and calculate volumes
df = df.fillna(0)
for c in ["height", "depth", "width"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

df["volume"] = df["height"] * df["depth"] * df["width"]
out = df[df["volume"] > 0][["name", "volume"]]

out.to_json("volumes.json", orient="records", force_ascii=False, indent=2)
print(f"✅ Done — generated volumes.json with {len(out)} items")
