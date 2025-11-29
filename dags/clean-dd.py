import pandas as pd
import numpy as np
import re
from datetime import datetime
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ================= CONFIG =================
INPUT_FILE = 'dags/ddproperty_bangkok_all_districts.csv'
OUTPUT_FILE = 'ddproperty_cleaned_ver6.csv'
TEST_MODE = True       # 🟢 True = ลอง 5 แถว | 🔴 False = ทำจริง
TEST_ROWS = 5
SAVE_INTERVAL = 100
# ==========================================

# Dict รหัสไปรษณีย์ (ใช้ชื่อเขตแบบไม่มีคำนำหน้าเป็น Key)
BKK_POSTCODES = {
    "พระนคร": "10200", "ดุสิต": "10300", "หนองจอก": "10530", "บางรัก": "10500", "บางเขน": "10220",
    "บางกะปิ": "10240", "ปทุมวัน": "10330", "ป้อมปราบศัตรูพ่าย": "10100", "พระโขนง": "10260", "มีนบุรี": "10510",
    "ลาดกระบัง": "10520", "ยานนาวา": "10120", "สัมพันธวงศ์": "10100", "พญาไท": "10400", "ธนบุรี": "10600",
    "บางกอกใหญ่": "10600", "ห้วยขวาง": "10310", "คลองสาน": "10600", "ตลิ่งชัน": "10170", "บางกอกน้อย": "10700",
    "บางขุนเทียน": "10150", "ภาษีเจริญ": "10160", "หนองแขม": "10160", "ราษฎร์บูรณะ": "10140", "บางพลัด": "10700",
    "ดินแดง": "10400", "บึงกุ่ม": "10240", "สาทร": "10120", "บางซื่อ": "10800", "จตุจักร": "10900",
    "บางคอแหลม": "10120", "ประเวศ": "10250", "คลองเตย": "10110", "สวนหลวง": "10250", "จอมทอง": "10150",
    "ดอนเมือง": "10210", "ราชเทวี": "10400", "ลาดพร้าว": "10230", "วัฒนา": "10110", "บางแค": "10160",
    "หลักสี่": "10210", "สายไหม": "10220", "คันนายาว": "10230", "สะพานสูง": "10240", "วังทองหลาง": "10310",
    "คลองสามวา": "10510", "บางนา": "10260", "ทวีวัฒนา": "10170", "ทุ่งครุ": "10140", "บางบอน": "10150"
}

print("📂 Loading Data...")
df = pd.read_csv(INPUT_FILE)

# 1. ลบข้อมูลซ้ำ
df.drop_duplicates(subset=['url'], keep='first', inplace=True)

# 2. ลบคอลัมน์ที่ไม่ต้องการทิ้ง
cols_to_drop = ['district_code', 'district_search_term']
df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

print(f"✅ Data count: {len(df)}")

# ------------------------------------------------

# --- CLEANING FUNCTIONS ---
def clean_money(val):
    if pd.isna(val) or str(val).strip() == '-': return np.nan
    val = str(val).replace('฿', '').replace(',', '').strip()
    val = val.split('/')[0].strip()
    try: return float(val)
    except: return np.nan

def clean_area(val):
    if pd.isna(val) or str(val).strip() == '-': return np.nan
    val = str(val).replace('ตร.ม.', '').replace(',', '').strip()
    try: return float(val)
    except: return np.nan

def clean_publish_date(text):
    if pd.isna(text): return np.nan
    text = str(text)
    match = re.search(r'([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})', text)
    if match:
        date_str = match.group(0)
        try:
            dt_obj = datetime.strptime(date_str, "%b %d, %Y")
            return dt_obj.strftime("%Y-%m-%d")
        except: return np.nan
    return np.nan

def extract_address_from_text(full_address):
    res = {'sub_district': np.nan, 'district': np.nan, 'province': 'กรุงเทพมหานคร', 'postcode': np.nan}
    if pd.isna(full_address): return res
    
    pc_match = re.search(r'\b10\d{3}\b', str(full_address))
    if pc_match: res['postcode'] = pc_match.group(0)

    parts = str(full_address).split(',')
    parts = [p.strip() for p in parts if p.strip() != '']
    if parts and 'ไทย' in parts[-1]: parts.pop() 
        
    if len(parts) >= 2:
        last_part = parts[-1]
        if 'กรุงเทพ' in last_part:
            if len(parts) >= 3:
                # remove 'เขต'/'แขวง' first to standardize
                res['district'] = parts[-2].replace('เขต', '').strip()
                res['sub_district'] = parts[-3].replace('แขวง', '').strip()
        else:
            res['district'] = parts[-1].replace('เขต', '').strip()
            if len(parts) >= 2:
                res['sub_district'] = parts[-2].replace('แขวง', '').strip()
    
    if pd.isna(res['postcode']) and pd.notna(res['district']):
        for d_key, d_code in BKK_POSTCODES.items():
            if d_key in res['district']:
                res['postcode'] = d_code
                break
    return res

# --- APPLY CLEANING ---
print("🧹 Cleaning columns...")
df['price'] = df['price'].apply(clean_money)
df['price_per_sqm'] = df['price_per_sqm'].apply(clean_money)
df['usable_area'] = df['usable_area'].apply(clean_area)
df['publish_date'] = df['publish_date'].apply(clean_publish_date)
df['floor'] = '-'

cols_geo = ['coords', 'latitude', 'longitude', 'sub_district', 'district', 'province', 'postcode']
for col in cols_geo:
    if col not in df.columns: df[col] = np.nan

# --- GEOPY LOGIC (Hybrid) ---
geolocator = Nominatim(user_agent="dd_hybrid_agent_final_v2", timeout=10)

def process_geopy_hybrid(full_address):
    final_res = {k: np.nan for k in cols_geo}
    final_res['province'] = "กรุงเทพมหานคร"
    
    # 1. Parse Text
    text_data = extract_address_from_text(full_address)
    final_res['sub_district'] = text_data['sub_district']
    final_res['district'] = text_data['district']
    final_res['postcode'] = text_data['postcode']

    # 2. Search Full Address
    location = None
    try:
        if pd.notna(full_address):
            location = geolocator.geocode(f"{full_address}, Thailand", language='th')
    except: pass

    # 3. Search Fallback (Keyword)
    if not location and pd.notna(final_res['district']):
        search_query = f"{final_res['sub_district'] or ''} {final_res['district']} กรุงเทพมหานคร"
        try:
            location = geolocator.geocode(search_query, language='th')
        except: pass

    if location:
        final_res['latitude'] = location.latitude
        final_res['longitude'] = location.longitude
        final_res['coords'] = f"{location.latitude},{location.longitude}"
        geo_postcode = location.raw.get('address', {}).get('postcode')
        if pd.isna(final_res['postcode']) and geo_postcode:
             final_res['postcode'] = geo_postcode

    return final_res

# --- 🔥 HELPER FUNCTIONS FOR PREFIX ---
def add_prefix_district(val):
    if pd.isna(val) or str(val).strip() == '': return np.nan
    val = str(val).strip()
    # ถ้ายังไม่มีคำว่า เขต ให้เติมเข้าไป
    if not val.startswith('เขต'):
        return f"เขต{val}"
    return val

def add_prefix_sub_district(val):
    if pd.isna(val) or str(val).strip() == '': return np.nan
    val = str(val).strip()
    # ถ้ายังไม่มีคำว่า แขวง ให้เติมเข้าไป
    if not val.startswith('แขวง'):
        return f"แขวง{val}"
    return val
# --------------------------------------

# --- RUN PROCESS ---
print(f"🌍 Starting Process (TEST_MODE={TEST_MODE})...")
rows_to_process = df.head(TEST_ROWS) if TEST_MODE else df

TARGET_COLUMNS = [
    'url', 'title', 'publish_date', 'price', 'price_per_sqm', 
    'usable_area', 'floor', 'bedroom', 'restroom', 
    'coords', 'full_address', 'sub_district', 'district', 
    'province', 'postcode', 'latitude', 'longitude'
]

for index, row in rows_to_process.iterrows():
    print(f"   [{index}] Processing: {str(row['full_address'])[:40]}...")
    geo_data = process_geopy_hybrid(row['full_address'])
    for col in cols_geo:
        df.at[index, col] = geo_data[col]
    
    if not TEST_MODE and (index + 1) % SAVE_INTERVAL == 0:
        df[TARGET_COLUMNS].to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"💾 Auto-saved at row {index}")
    
    time.sleep(1)

# --- 🔥 FINAL STEP: ADD PREFIX & FORMATTING ---
print("✨ Finalizing: Adding prefixes (เขต/แขวง)...")
final_df = df.head(TEST_ROWS) if TEST_MODE else df

# เติมคำว่า เขต / แขวง
final_df['district'] = final_df['district'].apply(add_prefix_district)
final_df['sub_district'] = final_df['sub_district'].apply(add_prefix_sub_district)

# กรอง Column สุดท้าย
final_df = final_df.reindex(columns=TARGET_COLUMNS)

final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print(f"\n✅ Done! Saved to {OUTPUT_FILE}")
if TEST_MODE:
    # โชว์ผลลัพธ์ให้ดู
    print(final_df[['publish_date', 'sub_district', 'district', 'postcode']].to_string())