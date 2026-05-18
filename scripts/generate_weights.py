import os
import pandas as pd
import requests
import io
import json

print("📦 Starting weights.json generation...")

# 1️⃣ Get URL from GitHub secret
csv_url = os.getenv("WEIGHTS_CSV_URL")
if not csv_url:
    raise RuntimeError("❌ WEIGHTS_CSV_URL secret not found")

print(f"🔗 Downloading CSV from: {csv_url[:50]}...")

# 2️⃣ Download the CSV file
response = requests.get(csv_url)
response.raise_for_status()

# 3️⃣ Parse CSV — semicolon separator, Windows-1250 encoding, comma decimal
try:
    df = pd.read_csv(
        io.BytesIO(response.content),
        sep=";",
        encoding="cp1250",
        dtype=str,          # read everything as string first
        quotechar='"',
    )
    print(f"✅ CSV loaded, {len(df)} rows.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to read CSV: {e}")

# 4️⃣ Normalize column names
df.columns = [str(c).strip().lower() for c in df.columns]
print("🧱 Columns:", df.columns.tolist())

# 5️⃣ Convert weight: replace comma → dot, coerce to float (kg)
df["weight"] = (
    df["weight"]
    .str.strip()
    .str.replace(",", ".", regex=False)
)
df["weight_kg"] = pd.to_numeric(df["weight"], errors="coerce")

# 6️⃣ Filter out rows with missing or zero weight
before = len(df)
df = df[df["weight_kg"].notna() & (df["weight_kg"] > 0)]
after = len(df)
print(f"🧹 Kept {after} rows with valid weight (skipped {before - after} empty/zero).")

# 7️⃣ Build output — weight stored in grams to match volumes.json convention
records = []
for _, row in df.iterrows():
    record = {
        "code": str(row["code"]).strip(),
        "name": str(row["name"]).strip(),
        "weight_g": round(row["weight_kg"] * 1000, 3),
    }
    records.append(record)

# 8️⃣ Save as JSON
os.makedirs("data", exist_ok=True)
output_file = "data/weights.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"💾 Saved {len(records)} products to {output_file}")
