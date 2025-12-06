# run "python -m uvicorn api:app"
# port 8000
# stop Control (⌃) + C
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from typing import Optional
import uvicorn
import os

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
CONDOS_FILE = "mock_condos.csv"
PROBLEM_FILE = "real_problems.csv"

# --- LOAD DATA (Run once when API starts) ---
# 1. Load Mock Condos
try:
    df_condos = pd.read_csv(CONDOS_FILE)
    # Clean NaN to prevent JSON errors
    df_condos = df_condos.fillna("") 
except FileNotFoundError:
    print("Please run mock_gen.py first to generate CSV files.")
    df_condos = pd.DataFrame()

# 2. Load Real Problems
if not os.path.exists(PROBLEM_FILE):
    print(f"❌ CRITICAL ERROR: File '{PROBLEM_FILE}' not found in current directory.")
    df_problems = pd.DataFrame()
else:
    try:
        print(f"📂 Found '{PROBLEM_FILE}', attempting to read...")
        try:
            df_problems = pd.read_csv(PROBLEM_FILE, encoding='utf-8')
            print("✅ Read with UTF-8")
        except UnicodeDecodeError:
            print("⚠️ UTF-8 failed, retrying with TIS-620...")
            df_problems = pd.read_csv(PROBLEM_FILE, encoding='tis-620')
            print("✅ Read with TIS-620")
            
        # Cleaning
        if 'lat' in df_problems.columns and 'lon' in df_problems.columns:
            df_problems['lat'] = pd.to_numeric(df_problems['lat'], errors='coerce')
            df_problems['lon'] = pd.to_numeric(df_problems['lon'], errors='coerce')
            initial_count = len(df_problems)
            df_problems = df_problems.dropna(subset=['lat', 'lon'])
            print(f"Dropped {initial_count - len(df_problems)} rows with invalid coordinates")
        df_problems = df_problems.replace([np.inf, -np.inf], np.nan)
        df_problems = df_problems.where(pd.notnull(df_problems), None)
        
        print(f"✅ Loaded Problems: {len(df_problems)} rows")

    except Exception as e:
        print(f"❌ Error loading problems: {e}")
        df_problems = pd.DataFrame()

@app.get("/")
def root():
    return {"message": "Urban Data API is running. Go to /docs to see endpoints."}

@app.get("/condo_data")
def get_condo_data(district: Optional[str] = None):
    # Get all Condos / Filter by District
    data = df_condos
    if not data.empty and district:
        data = data[data['district'] == district]
    return data.to_dict(orient="records")

@app.get("/problem_data")
def get_problem_data(limit: int = 20000):
    # Get all Traffy Fondue
    if df_problems.empty:
        return []
    # limit = 0 คือขอทั้งหมด (ช้า)
    if limit == 0 or limit >= len(df_problems):
        return df_problems.to_dict(orient="records")
    return df_problems.sample(n=limit).to_dict(orient="records")