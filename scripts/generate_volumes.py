import os
import pandas as pd
import requests

print("📦 Downloading XLS from:", os.getenv("CSV_URL"))

url = os.getenv("CSV_URL")
if not url:
    raise RuntimeError("❌ CSV_URL secret not found")

# Download the Excel file
response = requests.get(url)
response.raise_for_status()

# Save temporarily
with open("products.xls", "wb") as f:
    f.write(response.content)

# Read Excel instead of CSV
df = pd.read_excel("products.xls")

# Check columns
print("✅ Columns found:", df.columns.tolist())

# --- Adjust these column names if needed ---
height_col = "height"
depth_col = "depth"
width_col = "width"

# Compute volume in cubic meters
df["volume_m3"] = (df[height_col] * df[depth_col] * df[width_col]) / (100**3)

# Filter by max allowed volume (0.10044 m³)
max_volume = 0.10044
df_filtered = df[df["volume_m3"] <= max_volume]

# Only keep product name and volume
df_result = df_filtered[["name", "volume_m3"]]

# Save JSON
df_result.to_json("volumes.json", orient="records", indent=2, force_ascii=False)
print("✅ volumes.json successfully created")


