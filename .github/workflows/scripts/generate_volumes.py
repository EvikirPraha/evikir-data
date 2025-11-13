import os, pandas as pd, requests

CSV_URL = os.environ.get("CSV_URL")
if not CSV_URL:
    raise RuntimeError("CSV_URL env var is missing")

# download CSV
r = requests.get(CSV_URL, timeout=60)
r.raise_for_status()
with open("products.csv", "wb") as f:
    f.write(r.content)

# parse CSV (windows-1250, ;, comma decimals)
df = pd.read_csv("products.csv", encoding="windows-1250", sep=";", decimal=",")

# keep columns; missing -> 0
cols = ["name", "height", "depth", "width"]
missing = [c for c in cols if c not in df.columns]
if missing:
    raise RuntimeError(f"CSV missing columns: {missing}")

df2 = df[cols].copy().fillna(0)
for c in ["height", "depth", "width"]:
    df2[c] = pd.to_numeric(df2[c], errors="coerce").fillna(0)

# volume in m^3
df2["volume"] = df2["height"] * df2["depth"] * df2["width"]

# keep only >0 and write compact json
out = df2[df2["volume"] > 0][["name", "volume"]]
out.to_json("volumes.json", orient="records", force_ascii=False, indent=2)

print(f"✅ volumes.json written with {len(out)} items")
