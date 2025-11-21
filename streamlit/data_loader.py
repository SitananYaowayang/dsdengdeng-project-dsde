import pandas as pd
import numpy as np

# สุ่มข้อมูล 100 แถว
num_rows = 100
data = {
    'project_name': [f'Condo {i+1}' for i in range(num_rows)],
    'district': np.random.choice(['วัฒนา', 'ปทุมวัน', 'สาทร', 'ราชเทวี', 'ห้วยขวาง'], num_rows),
    'lat': np.random.uniform(13.70, 13.80, num_rows),
    'lon': np.random.uniform(100.50, 100.60, num_rows),
    'price_sqm': np.random.randint(80000, 250000, num_rows),
    'problem_count_500m': np.random.randint(1, 30, num_rows),
    'angry_score': np.round(np.random.uniform(0.1, 0.9, num_rows), 2),
    'livability_score': np.round(np.random.uniform(3.0, 9.5, num_rows), 2)
}

df = pd.DataFrame(data)

# บันทึกเป็น CSV
df.to_csv("mock.csv", index=False)
print("mock.csv created with 100 rows")
