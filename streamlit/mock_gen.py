# python mock_gen.py
import pandas as pd
import numpy as np

districts_bkk = [
    "พระนคร","ดุสิต","หนองจอก","บางรัก","บางเขน","บางกะปิ","ปทุมวัน","ป้อมปราบศัตรูพ่าย",
    "พระโขนง","มีนบุรี","ลาดกระบัง","ยานนาวา","สัมพันธวงศ์","พญาไท","ธนบุรี","บางกอกใหญ่",
    "ห้วยขวาง","คลองสาน","ตลิ่งชัน","บางกอกน้อย","บางขุนเทียน","ภาษีเจริญ","หนองแขม","ราษฎร์บูรณะ",
    "บางพลัด","ดินแดง","บึงกุ่ม","สาทร","บางซื่อ","จตุจักร","บางคอแหลม","ประเวศ","คลองเตย",
    "สวนหลวง","จอมทอง","ดอนเมือง","ราชเทวี","ลาดพร้าว","วัฒนา","บางแค","หลักสี่",
    "สายไหม","คันนายาว","สะพานสูง","วังทองหลาง","คลองสามวา","บางนา","ทวีวัฒนา","ทุ่งครุ","บางบอน"
]
problem_types = ['ถนน', 'ทางเท้า', 'ความปลอดภัย', 'แสงสว่าง', 'ความสะอาด', 'กีดขวาง', 'ท่อระบายน้ำ', 'น้ำท่วม', 'ต้นไม้', 'PM2.5', 'จราจร', 'สะพาน']
num_condos = 3000
num_problems = 10000 
np.random.seed(42)

# Generate Condo Data
condo_data = {
    "project_name": [f"Condo Project {i+1}" for i in range(num_condos)],
    "district": np.random.choice(districts_bkk, num_condos),
    "lat": np.random.uniform(13.65, 13.95, num_condos),
    "lon": np.random.uniform(100.35, 100.75, num_condos),
    "price_sqm": np.random.randint(70000, 350000, num_condos),
    "year": np.random.randint(2020, 2026, num_condos),
    "month": np.random.randint(1, 13, num_condos),

    # Aggregate fields
    "problem_count_500m": np.random.randint(1, 40, num_condos),
    "angry_score": np.round(np.random.uniform(0.1, 1.0, num_condos), 2),
    "livability_score": np.round(np.random.uniform(3.0, 9.5, num_condos), 2)
}
df_condo = pd.DataFrame(condo_data)
df_condo["date"] = pd.to_datetime(df_condo[["year", "month"]].assign(DAY=1))
df_condo.to_csv("mock_condos.csv", index=False)
print(f"Generated mock.csv with {num_condos} rows and 50 districts.")

# Generate City Problem Data
problem_data = {
    "ticket_id": [f"TF_{i+1:05d}" for i in range(num_problems)],
    "type": np.random.choice(problem_types, num_problems),
    "district": np.random.choice(districts_bkk, num_problems),
    "lat": np.random.uniform(13.65, 13.95, num_problems), # พิกัดควรกระจายคล้ายๆ คอนโด
    "lon": np.random.uniform(100.35, 100.75, num_problems),
    "status": np.random.choice(["รอการแก้ไข", "เสร็จสิ้น"], num_problems, p=[0.3, 0.7]),
    "sentiment_angry_score": np.round(np.random.uniform(0, 10, num_problems), 1) # from LLM
}
df_problems = pd.DataFrame(problem_data)
df_problems.to_csv("mock_problems.csv", index=False)
print(f"Generated mock_problems.csv ({num_problems} rows)")