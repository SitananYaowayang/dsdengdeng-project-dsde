import requests
from pathlib import Path
import pandas as pd

BASE_URL = "https://publicapi.traffy.in.th/teamchadchart-stat-api/download/bangkok_monthly"

NAME = "สิตานัน เยาวยัง"
ORG = "คณะวิศวกรรมศาสตร์ จุฬาฯ"
EMAIL = "sasitanan24@gmail.com"
PURPOSE = "ใช้ทำโปรเจกต์ Data Science CEDT"
PHONE = "0949418239"

# 1) ขอ list ไฟล์
params = {
    "name": NAME,
    "org": ORG,
    "email": EMAIL,
    "purpose": PURPOSE,
    "te": PHONE,
    "output_type": "json",
}

print("📡 Request file list...")
resp = requests.get(BASE_URL, params=params)
resp.raise_for_status()

files = resp.json()
print("📄 Available files:", files)

if not files:
    raise RuntimeError("ไม่พบไฟล์ใน API เลย")

# 2) เลือกไฟล์ล่าสุด (ถ้ามีหลายไฟล์ ใช้ timestamp มากสุด)
latest = max(files, key=lambda x: x["timestamp"])
file_name = latest["file_name"]        # เช่น 'bangkok_2021-09.csv'
download_url = latest["URL"]

print(f"🎯 Latest file: {file_name}")
print(f"🔗 Download URL: {download_url}")

# 3) ดาวน์โหลดไฟล์จาก URL โดยตรง

output_dir = Path(r"C:\Year_2\DSDE\dsdengdeng-project-dsde\data\raw\traffy-fondue")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / file_name   # เซฟชื่อเดียวกับที่ API ให้มา

print(f"⬇ Downloading to {output_path} ...")
download_resp = requests.get(download_url)
download_resp.raise_for_status()

with open(output_path, "wb") as f:
    f.write(download_resp.content)
 
print(f"✅ Download completed → {output_path}")


df = pd.read_csv(rf"C:\Year_2\DSDE\dsdengdeng-project-dsde\data\raw\traffy-fondue\{file_name}")


# คอลัมน์ที่ต้องการเอาไปใช้ (เรียงลำดับตามนี้)
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

final_df.to_csv(r"C:\Year_2\DSDE\dsdengdeng-project-dsde\data\raw\traffy-fondue\bangkok.csv", index=False, encoding='utf-8-sig')


 
