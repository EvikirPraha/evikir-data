import os
import pandas as pd
import requests
import io

CSV_URL = os.environ.get("CSV_URL")
if not CSV_URL:
    raise RuntimeError("❌ CSV_URL secret not found")

print("📦 Downloading CSV from:", CSV_URL)
r = requests.get(CSV_URL, timeout=60)
r.raise_for_status()
content = r.content

# Step 1️⃣: clean raw binary — remove NULs and other broken bytes
print("🧹 Cleaning raw CSV content")
cleaned = content.replace(b"\x00", b" ").replace(b"\r", b"").replace(b"\xa0", b" ")

# Step 2️⃣: decode text safely
try:
    text = cleaned.decode("utf-8", errors="ignore")
    encoding_used = "utf-8"
except Exception:
    text = cleaned.decode("iso8859_2", errors="ignore")
    encoding_used = "iso8859_2"

print(f"✅ Decoded using {encoding_used}")

# Step 3️⃣: normalize newlines & remove broken quotes
text = text.replace('""', '"').replace('";"', ';')
lines = [line for line in text.split("\n") if len(line.strip()) > 3]
cleaned_text = "\n".join(lines)

# Step 4️⃣: Try to load CSV
try:
    df = pd.read_csv(io.StringIO(cleaned_text), sep=";", decimal=",", on_bad_lines="skip", low_memory=False)
    print(f"✅ Parsed cleaned CSV successfully with {len(df)} rows")
except Exception as e:
    print("❌ Failed parsing even after cleaning:", e)
    raise

# Step 5️⃣: Compute volume
cols = ["name", "height", "depth", "width"]
for c in cols:
    if c not in df.columns:
        print(f"⚠️ Missing column '{c}', creating empty one")
        df[c] = 0

df = df.fillna(0)
for c in ["height", "depth", "width"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

df["volume"] = df["height"] * df["depth"] * df["width"]
out = df[df["volume"] > 0][["name", "volume"]]

out.to_json("volumes.json", orient="records", force_ascii=False, indent=2)
print(f"✅ Done — generated volumes.json with {len(out)} items")




