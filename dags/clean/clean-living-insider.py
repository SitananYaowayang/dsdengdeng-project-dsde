import pandas as pd
from datetime import datetime, timedelta
import re
import numpy as np
import os 

# --- Path Handling ---
base_dir = os.path.dirname(os.path.abspath(__file__))
# ตรวจสอบ path ให้แน่ใจว่าถูกต้อง
df1 = pd.read_csv("data/raw/living_insider_full_data_p3.csv")
df2 = pd.read_csv("data/raw/living_insider_full_data_ver1.csv")
df3 = pd.read_csv("data/raw/living_insider_full_data_districts.csv")

df = pd.concat([df1, df2, df3], ignore_index=True)

print(f"จำนวนแถวใน df1: {len(df1)}")
print(f"จำนวนแถวใน df2: {len(df2)}")
print(f"จำนวนแถวใน df_combined: {len(df)}")
# ---------------------

# 1. Clean basics & Filter
print(f"Rows before drop na: {len(df)}") 
df.dropna(subset=['full_address'], inplace=True)
df.dropna(subset=['price'], inplace=True)
df = df[df['province'] == 'กรุงเทพมหานคร'].copy()
print(f"Rows after drop na: {len(df)}") 

# ==========================================
print(f"Rows before drop duplicates: {len(df)}") 
df.drop_duplicates(subset=['url'], keep='first', inplace=True)
print(f"Rows after drop duplicates: {len(df)}") 

# ==========================================

TODAY = datetime.now().date() 

# --- 2. จัดการวันที่ (Relative Dates) ---
df.loc[df['publish_date'].astype(str).str.contains('ชั่วโมง|นาที|ชั่ว', na=False, regex=True, flags=re.IGNORECASE), 'publish_date'] = TODAY
df.loc[df['publish_date'].astype(str).str.contains('เมื่อวาน', na=False), 'publish_date'] = TODAY - timedelta(days=1)

for days_ago in range(2, 7):
    search_text = f'{days_ago} วันที่แล้ว'
    target_date = TODAY - timedelta(days=days_ago)
    df.loc[df['publish_date'].astype(str).str.contains(search_text, na=False), 'publish_date'] = target_date

df.loc[df['publish_date'].astype(str).str.contains('1? อาทิตย์ที่แล้ว', na=False, regex=True), 'publish_date'] = TODAY - timedelta(days=7)

# --- 3. แปลง พ.ศ. -> ค.ศ. ---
def buddhist_to_ad_converter(date_value):
    if isinstance(date_value, str):
        if re.match(r'^\d{1,2}/\d{1,2}/25\d{2}$', date_value):
            try:
                day, month, year = date_value.split('/')
                ad_year = int(year) - 543
                return f"{day}/{month}/{ad_year}"
            except ValueError:
                return date_value
    return date_value

df['publish_date'] = df['publish_date'].apply(buddhist_to_ad_converter)

# --- 4. แปลง Type ข้อมูล ---
df['publish_date'] = pd.to_datetime(df['publish_date'], format='%d/%m/%Y', errors='coerce')

df['price_per_sqm'] = (
    df['price_per_sqm']
    .astype(str)
    .str.replace(r'[^\d,]+', '', regex=True)
    .str.replace(',', '', regex=False)
    .replace('nan', np.nan)
    .astype(float)
)

df['price'] = (
    df['price']
    .astype(str)
    .str.replace('฿', '', regex=False)
    .str.replace(',', '', regex=False)
    .replace('nan', pd.NA)
    .astype(float)
)

df['usable_area'] = (
    df['usable_area']
    .astype(str)
    .str.replace(r'[^\d.]', '', regex=True) 
    .str.replace(r'\.{2,}', '.', regex=True)
    .str.strip('.') 
    .replace('nan', pd.NA)
    .astype(float)
)

# --- 5. แยก coords เป็น latitude, longitude ---
lat_long_split = df['coords'].str.split(',', expand=True)
if len(lat_long_split.columns) >= 2:
    df['latitude'] = lat_long_split[0]
    df['longitude'] = lat_long_split[1]
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
else:
    df['latitude'] = np.nan
    df['longitude'] = np.nan

# --- 6. จัดการเติมคำว่า "เขต" ---
if 'district' in df.columns:
    df['district'] = df['district'].astype(str).str.strip()
    
    # Check sub_district เพื่อแก้ district ให้ถูกต้องตามเงื่อนไขพิเศษ
    if 'sub_district' in df.columns:
        df['sub_district'] = df['sub_district'].astype(str).str.strip()
        
        # 1. กรณีแขวงมีนบุรี -> เขตมีนบุรี
        df.loc[df['sub_district'] == 'แขวงมีนบุรี', 'district'] = 'เขตมีนบุรี'
        
        # 2. กรณีแขวงบางมด -> เขตบางมด (เพิ่มใหม่)
        df.loc[df['sub_district'] == 'แขวงบางมด', 'district'] = 'เขตบางมด'

    # เติมคำว่า 'เขต' สำหรับรายการที่ยังไม่มี
    condition = (~df['district'].str.startswith('เขต')) & (df['district'] != 'nan')
    df.loc[condition, 'district'] = 'เขต' + df.loc[condition, 'district']

# ==========================================

output_file_path = "data/processed/living_insider_BKK_processed_ver4.csv"
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

df.to_csv(output_file_path, index=False)
print("Done.")