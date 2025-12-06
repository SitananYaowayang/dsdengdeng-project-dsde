import pandas as pd
import numpy as np
import re  # <--- 1. ต้อง import re เข้ามาด้วยครับ

# ================= CONFIG =================
INPUT_FILE = '\data\processed\ddproperty\ddproperty_cleaned_ver4_prefix.csv'
OUTPUT_FILE = '\data\processed\ddproperty\ddproperty_processed.csv'
# ==========================================

print(f"📂 กำลังอ่านไฟล์: {INPUT_FILE}")
df = pd.read_csv(INPUT_FILE)
df.drop('floor', axis=1, inplace=True, errors='ignore')  # ลบคอลัมน์ floor ทิ้งถ้ามี
# --- CLEANING FUNCTION ---
def clean_location_prefix(val):
    # 1. เช็คค่าว่าง หรือ NaN
    if pd.isna(val) or str(val).strip() == '' or str(val).strip() == '-': 
        return np.nan
    
    val_str = str(val).strip()
    
    # 2. ใช้ Regex ลบคำนำหน้า
    # ลบคำว่า เขต, แขวง, อำเภอ, ตำบล ที่อยู่หน้าสุดออก
    val_cleaned = re.sub(r'^(เขต|แขวง|อำเภอ|ตำบล|อ\.|ต\.)', '', val_str)
    
    return val_cleaned.strip()

# --- เริ่มทำงาน ---
print("⚙️ กำลังคลีนข้อมูล (ลบคำนำหน้า เขต/แขวง)...")

def clean_bedroom(val):
    if pd.isna(val) or str(val).strip() == '-': return np.nan
    val_str = str(val).strip()
    
    # 1. จัดการกรณี 'สตูดิโอ' หรือ 'Studio' -> ให้เป็น 0
    if 'สตูดิโอ' in val_str or 'studio' in val_str.lower():
        return 1.0
    
    # 2. จัดการกรณีตัวเลขบวกกัน (เช่น 3+1, 7+4) หรือตัวเลขปกติ
    # ใช้ Regex ดึงตัวเลขทั้งหมดออกมา แล้วจับบวกกัน
    # วิธีนี้รองรับทั้ง "3", "3+1", "3 + 1" หรือแม้แต่ "Penthouse 4" (ถ้ามีเลข 4 หลุดมา)
    numbers = re.findall(r'\d+', val_str)
    if numbers:
        # แปลงเป็น int แล้วบวกกัน (เช่น ['3', '1'] -> 4)
        total_rooms = sum(int(n) for n in numbers)
        return float(total_rooms)
        
    return np.nan

df['bedroom'] = df['bedroom'].apply(clean_bedroom)

# 1. จัดการ District (เขต)
if 'district' in df.columns:
    # 2. แก้ตรงนี้ให้เรียกใช้ฟังก์ชัน clean_location_prefix
    df['district'] = df['district'].apply(clean_location_prefix)

# 2. จัดการ Sub-district (แขวง)
if 'sub_district' in df.columns:
    # 3. แก้ตรงนี้ให้เรียกใช้ฟังก์ชัน clean_location_prefix
    df['sub_district'] = df['sub_district'].apply(clean_location_prefix)

# --- บันทึกไฟล์ ---
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print(f"✅ เรียบร้อย! บันทึกไฟล์ใหม่ชื่อ: {OUTPUT_FILE}")

# --- แสดงตัวอย่างผลลัพธ์ ---
print("\n--- ตัวอย่างข้อมูล 5 แถวแรก ---")
print(df[['sub_district', 'district']].head(5).to_string())