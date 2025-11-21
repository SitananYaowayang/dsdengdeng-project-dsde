import pandas as pd
from datetime import datetime, timedelta
import re
import numpy as np

df = pd.read_csv("data/raw/living_insider_full_data_p3.csv")

df.dropna(subset=['full_address'], inplace=True)
df.dropna(subset=['price'], inplace=True)
df = df[df['province'] == 'กรุงเทพมหานคร'].copy()
# 1. กำหนดวันปัจจุบัน (Current Date) โดยดึงจากระบบ
# เนื่องจากวันนี้คือ 20/11/2568 โค้ดจะใช้ค่านี้เป็นฐานในการคำนวณ
TODAY = datetime.now().date() 

### 2. การแทนที่คำที่เป็น Relative Dates (สำหรับค่าที่ยังเป็น String อยู่) ###

# 2.1 แทนที่คำที่มี "ชั่วโมง" หรือ "นาที" ด้วยวันปัจจุบัน
# ใช้ re.IGNORECASE เพื่อครอบคลุม 'ชั่วโมง' และ 'ชั่ว'
df.loc[df['publish_date'].astype(str).str.contains('ชั่วโมง|นาที|ชั่ว', na=False, regex=True, flags=re.IGNORECASE), 'publish_date'] = TODAY

# 2.2 แทนที่ "เมื่อวาน" (1 วันที่แล้ว)
df.loc[df['publish_date'].astype(str).str.contains('เมื่อวาน', na=False), 'publish_date'] = TODAY - timedelta(days=1)

# 2.3 แทนที่ "X วันที่แล้ว" (2-6 วันที่แล้ว)
for days_ago in range(2, 7):
    # สร้างข้อความค้นหา เช่น '2 วันที่แล้ว'
    search_text = f'{days_ago} วันที่แล้ว'
    
    # คำนวณวันที่ที่ถูกต้อง
    target_date = TODAY - timedelta(days=days_ago)
    
    # แทนที่
    df.loc[df['publish_date'].astype(str).str.contains(search_text, na=False), 'publish_date'] = target_date

# 2.4 แทนที่ "X อาทิตย์ที่แล้ว" (7 วันที่แล้ว)
# ใช้ regex '1? ' เพื่อครอบคลุมทั้ง '1 อาทิตย์ที่แล้ว' และ 'อาทิตย์ที่แล้ว'
df.loc[df['publish_date'].astype(str).str.contains('1? อาทิตย์ที่แล้ว', na=False, regex=True), 'publish_date'] = TODAY - timedelta(days=7)


### 3. การแปลงวันที่จาก พ.ศ. เป็น ค.ศ. (สำหรับค่าที่ยังเป็น DD/MM/YYYY)

# ฟังก์ชันสำหรับแปลงปี พ.ศ. (25xx) ให้เป็น ค.ศ. (20xx) โดยการลบ 543
def buddhist_to_ad_converter(date_value):
    if isinstance(date_value, str):
        # ตรวจสอบรูปแบบ DD/MM/YYYY ที่ใช้ปี พ.ศ. (เช่น 2568)
        if re.match(r'^\d{1,2}/\d{1,2}/25\d{2}$', date_value):
            try:
                day, month, year = date_value.split('/')
                ad_year = int(year) - 543
                return f"{day}/{month}/{ad_year}"
            except ValueError:
                return date_value # คืนค่าเดิมหากการแยกส่วนผิดพลาด
    return date_value

# ใช้ .apply() เพื่อแปลงค่าวันที่ที่เป็น String ในรูปแบบ พ.ศ.
df['publish_date'] = df['publish_date'].apply(buddhist_to_ad_converter)


### 4. แปลงคอลัมน์ทั้งหมดให้เป็น Datetime Object ที่สมบูรณ์

# แปลงคอลัมน์ 'publish_date' ทั้งหมดเป็นชนิดข้อมูล Datetime
# ค่าที่ถูกแทนที่ด้วย TODAY จะถูกแปลงอย่างถูกต้อง
# ค่าที่ยังเป็น String (ที่แปลงเป็น ค.ศ. แล้ว) จะถูกแปลงตาม format='%d/%m/%Y'
df['publish_date'] = pd.to_datetime(
    df['publish_date'], 
    format='%d/%m/%Y', 
    errors='coerce'
)
df['price_per_sqm'] = (
    df['price_per_sqm']
    .astype(str) # 1. แปลงเป็น string ก่อนเพื่อป้องกัน error ในการใช้ .str
    .str.replace(r'[^\d,]+', '', regex=True) # 2. ใช้ regex ลบทุกอักขระที่ไม่ใช่ตัวเลข (\d) หรือคอมมา (,)
    .str.replace(',', '', regex=False) # 3. ลบคอมมา (,) ซึ่งเป็นตัวคั่นหลักพัน
    .replace('nan', np.nan) # 4. จัดการกับค่า 'nan' ที่อาจเกิดจากการแปลง string
    .astype(float) # 5. แปลงข้อมูลที่เหลือให้เป็นตัวเลขทศนิยม (float)
)

df.drop_duplicates(subset=['url'], keep='first', inplace=True)

df['price'] = (
    df['price']
    .astype(str) # แปลงเป็น string ก่อนเพื่อความปลอดภัยในการใช้ .str
    .str.replace('฿', '', regex=False) # ลบสัญลักษณ์ '฿'
    .str.replace(',', '', regex=False) # ลบเครื่องหมายคอมมา ','
    .replace('nan', pd.NA) # จัดการกับค่า 'nan' ที่อาจแปลงมาจาก string
    .astype(float) # แปลงเป็นตัวเลขทศนิยม (float)
)

df['usable_area'] = (
    df['usable_area']
    .astype(str)
    # 1. ลบอักขระที่ไม่ใช่ตัวเลขหรือจุดทศนิยม
    .str.replace(r'[^\d.]', '', regex=True) 
    
    # 2. <<< เพิ่มบรรทัดนี้เพื่อจัดการจุดซ้ำซ้อน! >>>
    # ใช้ regex เพื่อแทนที่จุดทศนิยมที่ตามมาด้วยจุดทศนิยมอื่น (เช่น '..', '...') ให้เหลือแค่จุดเดียว
    .str.replace(r'\.{2,}', '.', regex=True) # แทนที่จุดทศนิยม 2 จุดขึ้นไป ด้วยจุดทศนิยม 1 จุด
    
    # 3. ลบจุดทศนิยมที่อยู่ตอนท้ายหรือตอนต้น (เช่น '.30.45' -> '30.45' หรือ '30.45.' -> '30.45')
    .str.strip('.') 
    
    .replace('nan', pd.NA)
    .astype(float) # บรรทัดนี้ควรทำงานได้แล้ว
)

output_file_path = "data/processed/living_insider_BKK_processed_02.csv"
df.to_csv(output_file_path, index=False)