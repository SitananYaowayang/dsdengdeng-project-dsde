import requests
from pathlib import Path

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

output_dir = Path(r"C:\Users\sasit\CU\2-1\dsde\project\dsdengdeng-project-dsde\data\raw\traffy-fondue")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / file_name   # เซฟชื่อเดียวกับที่ API ให้มา

print(f"⬇ Downloading to {output_path} ...")
download_resp = requests.get(download_url)
download_resp.raise_for_status()

with open(output_path, "wb") as f:
    f.write(download_resp.content)
 
print(f"✅ Download completed → {output_path}")
