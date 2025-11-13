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

# Try multiple parsing methods
df = None
errors = []

# 1️⃣ Try direct read_csv with normal encodings
for enc in ["windows-1250", "windows-1252", "latin-2", "utf-8-sig"]:
    try:
        df = pd.read_csv(io.BytesIO(content), encoding=enc, sep=";", decimal=",", on_bad_lines="skip")
        print(f"✅ Loaded CSV with encoding {enc}")
        break
    except Exception as e:
        errors.append(f"{enc}: {e}")

# 2️⃣ Fallback: try reading as binary text ignoring invalid bytes
if df is None:
    try:
        text = content.decode("latin-2", errors="ignore")
        df = pd.read_csv(io.StringIO(text), sep=";", decimal=",", on_bad_lines="skip")
        print("✅ Loaded CSV with binary fallback (latin-2, errors ignored)")
    except Exception as e:
        errors.append(f"binary fallback: {e}")

# 3️⃣ If still failed, show diagnostics
if df is None:
    raise RuntimeError("❌ Could not read CSV file. Tried:\n" + "\n".join(errors))

# Check columns
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


out.to_json("volumes.json", orient="records", force_ascii=False, indent=2)
print(f"✅ Done — generated volumes.json with {len(out)} items")


