import pandas as pd
import numpy as np

# 50 เขตกรุงเทพมหานคร
districts_bkk = [
    "พระนคร","ดุสิต","หนองจอก","บางรัก","บางเขน","บางกะปิ","ปทุมวัน","ป้อมปราบศัตรูพ่าย",
    "พระโขนง","มีนบุรี","ลาดกระบัง","ยานนาวา","สัมพันธวงศ์","พญาไท","ธนบุรี","บางกอกใหญ่",
    "ห้วยขวาง","คลองสาน","ตลิ่งชัน","บางกอกน้อย","บางขุนเทียน","ภาษีเจริญ","หนองแขม","ราษฎร์บูรณะ",
    "บางพลัด","ดินแดง","บึงกุ่ม","สาทร","บางซื่อ","จตุจักร","บางคอแหลม","ประเวศ","คลองเตย",
    "สวนหลวง","จอมทอง","ดอนเมือง","ราชเทวี","ลาดพร้าว","วัฒนา","บางแค","หลักสี่",
    "สายไหม","คันนายาว","สะพานสูง","วังทองหลาง","คลองสามวา","บางนา","ทวีวัฒนา","ทุ่งครุ","บางบอน"
]

# จำนวนแถว mock
num_rows = 3000

# สุ่มเขตจาก 50 เขต
districts = np.random.choice(districts_bkk, num_rows)

# สุ่ม lat, lon ในกรุงเทพ (ช่วงประมาณ)
latitudes  = np.random.uniform(13.65, 13.95, num_rows)
longitudes = np.random.uniform(100.35, 100.75, num_rows)

data = {
    "project_name": [f"Condo Project {i+1}" for i in range(num_rows)],
    "district": districts,
    "lat": latitudes,
    "lon": longitudes,

    # ราคาเฉลี่ยต่อตร.ม.
    "price_sqm": np.random.randint(70000, 350000, num_rows),

    # ปัญหาเมือง (Traffy)
    "problem_count_500m": np.random.randint(1, 40, num_rows),
    "angry_score": np.round(np.random.uniform(0.1, 1.0, num_rows), 2),

    # Livability score
    "livability_score": np.round(np.random.uniform(3.0, 9.5, num_rows), 2),

    # เวลา
    "year": np.random.randint(2020, 2026, num_rows),
    "month": np.random.randint(1, 13, num_rows)
}

df = pd.DataFrame(data)
df["date"] = pd.to_datetime(df[["year", "month"]].assign(DAY=1))

df.to_csv("mock2.csv", index=False)
print(f"mock.csv created with {num_rows} rows and 50 districts.")
