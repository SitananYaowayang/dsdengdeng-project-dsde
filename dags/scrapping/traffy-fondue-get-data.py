import requests
from pathlib import Path
import pandas as pd

# ============================================
# 🔧 0) Define Project Root Automatically
# ============================================
# ไฟล์นี้อยู่ที่:  dags/scrapping/traffy-fondue-get-data.py
# เราต้องการ root ไปที่โฟลเดอร์โปรเจกต์
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "traffy-fondue"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = RAW_DIR / "bangkok.csv"

print("📂 Project root =", PROJECT_ROOT)
print("📂 RAW data dir =", RAW_DIR)
print()

# ============================================
# 📡 1) Call API
# ============================================

BASE_URL = "https://publicapi.traffy.in.th/teamchadchart-stat-api/download/bangkok_monthly"

NAME = "สิตานัน เยาวยัง"
ORG = "คณะวิศวกรรมศาสตร์ จุฬาฯ"
EMAIL = "sasitanan24@gmail.com"
PURPOSE = "ใช้ทำโปรเจกต์ Data Science CEDT"
PHONE = "0949418239"

params = {
    "name": NAME,
    "org": ORG,
    "email": EMAIL,
    "purpose": PURPOSE,
    "te": PHONE,
    "output_type": "json",
}

print("📡 Requesting file list...")
resp = requests.get(BASE_URL, params=params)
resp.raise_for_status()

files = resp.json()
print("📄 Available files:", files)

if not files:
    raise RuntimeError("❌ ไม่พบไฟล์ใน API เลย")

# ============================================
# 🎯 2) Pick the latest file
# ============================================
latest = max(files, key=lambda x: x["timestamp"])
file_name = latest["file_name"]
download_url = latest["URL"]

print(f"🎯 Latest file: {file_name}")
print(f"🔗 URL: {download_url}")

# ============================================
# ⬇ 3) Download into /data/raw/traffy-fondue
# ============================================
output_path = RAW_DIR / file_name

print(f"⬇ Downloading → {output_path}")
download_resp = requests.get(download_url)
download_resp.raise_for_status()

with open(output_path, "wb") as f:
    f.write(download_resp.content)

print("✅ Downloaded successfully!")
print()

# ============================================
# 🧹 4) Load & keep selected columns
# ============================================
df = pd.read_csv(output_path)

TARGET_COLUMNS = [
    "ticket_id",
    "type",
    "organization",
    "comment",
    "photo",
    "photo_after",
    "coords",
    "address",
    "subdistrict",
    "district",
    "province",
    "timestamp",
    "state",
    "star",
    "count_reopen",
    "last_activity"
]

final_df = df.reindex(columns=TARGET_COLUMNS)

# ============================================
# 💾 5) Export cleaned CSV for next pipeline
# ============================================
final_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

print(f"🎉 Saved cleaned CSV → {OUTPUT_CSV}")
