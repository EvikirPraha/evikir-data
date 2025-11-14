import os
import pandas as pd
import requests
import io
import json

print("📦 Starting volumes.json generation...")

# 1️⃣ Get URL from GitHub secret
csv_url = os.getenv("CSV_URL")
if not csv_url:
    raise RuntimeError("❌ CSV_URL secret not found")

print(f"🔗 Downloading XLS from: {csv_url[:50]}...")

# 2️⃣ Download the Excel file
response = requests.get(csv_url)
response.raise_for_status()

# 3️⃣ Load into pandas DataFrame
try:
    df = pd.read_excel(io.BytesIO(response.content))
    print(f"✅ Excel loaded, {len(df)} rows.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to read Excel file: {e}")

# 4️⃣ Try to detect relevant columns
df.columns = [str(c).strip().lower() for c in df.columns]
print("🧱 Columns:", df.columns.tolist())

possible_names = {
    "width": ["šířka", "sirka", "width"],
    "height": ["výška", "vyska", "height"],
    "depth": ["hloubka", "depth"]
}

def find_col(name_options):
    for col in df.columns:
        for option in name_options:
            if option in col:
                return col
    return None

w_col = find_col(possible_names["width"])
h_col = find_col(possible_names["height"])
d_col = find_col(possible_names["depth"])

if not all([w_col, h_col, d_col]):
    print("⚠️ Could not detect all dimensions automatically.")
    print(f"Width: {w_col}, Height: {h_col}, Depth: {d_col}")
else:
    print(f"✅ Found dimension columns: {w_col}, {h_col}, {d_col}")

# 5️⃣ Compute volume if possible
if all([w_col, h_col, d_col]):
    df["volume_cm3"] = df[w_col] * df[h_col] * df[d_col]
else:
    df["volume_cm3"] = None

# 6️⃣ Save as JSON
os.makedirs("data", exist_ok=True)
output_file = "data/volumes.json"

data = df.to_dict(orient="records")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"💾 Saved {len(df)} rows to {output_file}")



