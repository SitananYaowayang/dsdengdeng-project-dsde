import pandas as pd
import numpy as np

# ================= ตั้งค่าชื่อไฟล์ตรงนี้ =================
INPUT_FILE = 'ddproperty_cleaned_ver5.csv'  # ชื่อไฟล์เดิมของคุณ
OUTPUT_FILE = 'ddproperty_cleaned_ver4_prefix.csv' # ชื่อไฟล์ใหม่ที่จะเซฟ
# ====================================================

print(f"📂 กำลังอ่านไฟล์: {INPUT_FILE}")
df = pd.read_csv(INPUT_FILE)

# --- ฟังก์ชันเติมคำนำหน้า ---
def add_prefix_district(val):
    """ เติมคำว่า 'เขต' ถ้ายังไม่มี """
    if pd.isna(val) or str(val).strip() == '': return np.nan
    val = str(val).strip()
    
    # เช็คว่ามีคำว่า เขต อยู่หน้าสุดหรือยัง
    if not val.startswith('เขต'):
        return f"เขต{val}"
    return val

def add_prefix_sub_district(val):
    """ เติมคำว่า 'แขวง' ถ้ายังไม่มี """
    if pd.isna(val) or str(val).strip() == '': return np.nan
    val = str(val).strip()
    
    # เช็คว่ามีคำว่า แขวง อยู่หน้าสุดหรือยัง
    if not val.startswith('แขวง'):
        return f"แขวง{val}"
    return val

# --- เริ่มทำงาน ---
print("⚙️ กำลังเติมคำนำหน้า...")

# 1. จัดการ District (เขต)
if 'district' in df.columns:
    df['district'] = df['district'].apply(add_prefix_district)

# 2. จัดการ Sub-district (แขวง)
if 'sub_district' in df.columns:
    df['sub_district'] = df['sub_district'].apply(add_prefix_sub_district)

# --- บันทึกไฟล์ ---
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print(f"✅ เรียบร้อย! บันทึกไฟล์ใหม่ชื่อ: {OUTPUT_FILE}")

# --- แสดงตัวอย่างผลลัพธ์ ---
print("\n--- ตัวอย่างข้อมูล 5 แถวแรก ---")
print(df[['sub_district', 'district']].head(5).to_string())