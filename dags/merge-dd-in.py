import pandas as pd
import numpy as np
import re

# ================= CONFIG =================
FILE_LIVING = 'dags/living_insider_BKK_processed_ver4.csv'
FILE_DD = 'dags/ddproperty_cleaned_ver4_prefix.csv'

OUTPUT_FILE = 'dags/merged_real_estate_data_1.csv'          # ไฟล์ผลลัพธ์ (Clean)
OUTPUT_REMOVED = 'dags/removed_duplicates_log.csv'        # 🔥 ไฟล์เก็บตัวที่โดนตัดทิ้ง
# ==========================================

print("📂 Loading files...")
try: df_living = pd.read_csv(FILE_LIVING, encoding='utf-8')
except: df_living = pd.read_csv(FILE_LIVING, encoding='utf-8-sig')

try: df_dd = pd.read_csv(FILE_DD, encoding='utf-8')
except: df_dd = pd.read_csv(FILE_DD, encoding='utf-8-sig')

# ใส่ Source
df_living['source'] = 'LivingInsider'
df_dd['source'] = 'DDProperty'

# --- TITLE NORMALIZATION ---
def normalize_title(title):
    if pd.isna(title): return ""
    title = str(title)
    if ':' in title:
        title = title.split(':')[-1]
    clean_text = re.sub(r'[\s\-\,\.\(\)]+', '', title)
    return clean_text.lower()

print("⚙️ Normalizing titles...")
df_living['norm_title'] = df_living['title'].apply(normalize_title)
df_dd['norm_title'] = df_dd['title'].apply(normalize_title)

# --- MERGE ---
common_cols = [
    'url', 'title', 'norm_title', 'publish_date', 'price', 'price_per_sqm', 
    'usable_area', 'floor', 'bedroom', 'restroom', 
    'full_address', 'sub_district', 'district', 'province', 'postcode', 
    'latitude', 'longitude', 'coords', 'source'
]

df_living = df_living.reindex(columns=common_cols)
df_dd = df_dd.reindex(columns=common_cols)

# เอา Living ขึ้นก่อน (เพื่อให้ Living เป็นตัวหลัก)
df_merged = pd.concat([df_living, df_dd], ignore_index=True)

# --- 🔥 SPLIT DUPLICATES (แก้ตรงนี้) ---
subset_check = ['norm_title', 'price', 'usable_area']

# 1. หาว่าแถวไหนซ้ำบ้าง (True = ซ้ำ, False = ตัวแรก/ไม่ซ้ำ)
# keep='first' แปลว่า ตัวแรกที่เจอจะ False (เก็บไว้) ตัวถัดๆ มาที่เหมือนกันจะ True (คือตัวซ้ำ)
dup_mask = df_merged.duplicated(subset=subset_check, keep='first')

# 2. แยกข้อมูลออกเป็น 2 ส่วน
df_removed = df_merged[dup_mask].copy()   # ข้อมูลที่โดนตัดออก
df_final = df_merged[~dup_mask].copy()    # ข้อมูลที่เหลืออยู่ (~ คือ not)

print(f"📊 ข้อมูลทั้งหมด: {len(df_merged)} แถว")
print(f"❌ ตัดออก (ซ้ำ): {len(df_removed)} แถว")
print(f"✅ เหลือใช้จริง: {len(df_final)} แถว")

# Cleanup
df_final.drop(columns=['norm_title'], inplace=True)
df_removed.drop(columns=['norm_title'], inplace=True)

# Save Files
df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
df_removed.to_csv(OUTPUT_REMOVED, index=False, encoding='utf-8-sig')

print(f"\n💾 บันทึกไฟล์หลักที่: {OUTPUT_FILE}")
print(f"🗑️ บันทึกไฟล์ตัวซ้ำที่: {OUTPUT_REMOVED}")