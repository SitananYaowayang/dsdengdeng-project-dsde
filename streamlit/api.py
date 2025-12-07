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
CONDOS_FILE = "condo.csv"
# PROBLEM_FILE = "problem.csv"
PROBLEM_SUMMARY_FILE = "problem_summary.csv"
DISTRICT_SUMMARY_FILE = "district_summary.csv"

# --- LOAD DATA (Run once when API starts) ---
# 1. Load Condos
print(f"📂 '{CONDOS_FILE}', attempting to read...")
try:
    df_condo = pd.read_csv(CONDOS_FILE, encoding='utf-8')
    print("✅ Read with UTF-8")
except UnicodeDecodeError:
    print("⚠️ UTF-8 failed, retrying with TIS-620...")
    df_condo = pd.read_csv(CONDOS_FILE, encoding='tis-620')
    print("✅ Read with TIS-620")
# Cleaning
if 'district_cleaned' in df_condo.columns:
    df_condo.rename(columns={'district_cleaned': 'district_original'}, inplace=True)
    # The first 'district' column in the mock data is the one to keep, let's just clean the numeric types
# Ensure key numeric columns are properly typed
numeric_cols = ['price', 'price_per_sqm', 'usable_area', 'bedroom', 'restroom', 'Livability_Score_10']
for col in numeric_cols:
    if col in df_condo.columns:
        df_condo[col] = pd.to_numeric(df_condo[col], errors='coerce')
# Clean up infinite values and replace with None (for JSON serialization)
df_condo = df_condo.replace([np.inf, -np.inf], np.nan)
df_condo = df_condo.where(pd.notnull(df_condo), None)
print(f"✅ Loaded Condos: {len(df_condo)} rows")

# 2. Load Problems
# print(f"📂 '{PROBLEM_FILE}', attempting to read...")
# try:
#     df_problem = pd.read_csv(PROBLEM_FILE, encoding='utf-8')
#     print("✅ Read with UTF-8")
# except UnicodeDecodeError:
#     print("⚠️ UTF-8 failed, retrying with TIS-620...")
#     df_problem = pd.read_csv(PROBLEM_FILE, encoding='tis-620')
#     print("✅ Read with TIS-620")
# # Cleaning
# if 'lat' in df_problem.columns and 'lon' in df_problem.columns:
#     df_problem['lat'] = pd.to_numeric(df_problem['lat'], errors='coerce')
#     df_problem['lon'] = pd.to_numeric(df_problem['lon'], errors='coerce')
#     initial_count = len(df_problem)
#     df_problem = df_problem.dropna(subset=['lat', 'lon'])
#     # print(f"Dropped {initial_count - len(df_problem)} rows with invalid coordinates")
# df_problem = df_problem.replace([np.inf, -np.inf], np.nan)
# df_problem = df_problem.where(pd.notnull(df_problem), None)
# print(f"✅ Loaded Problems: {len(df_problem)} rows")

# 3. Load Problem Summary
print(f"📂 '{PROBLEM_SUMMARY_FILE}', attempting to read...")
try:
    df_prob_summary = pd.read_csv(PROBLEM_SUMMARY_FILE, encoding='utf-8')
    print("✅ Read with UTF-8")
except UnicodeDecodeError:
    print("⚠️ UTF-8 failed, retrying with TIS-620...")
    df_prob_summary = pd.read_csv(PROBLEM_SUMMARY_FILE, encoding='tis-620')
    print("✅ Read with TIS-620")
print(f"✅ Loaded Problem Summary: {len(df_prob_summary)} rows")

# 4. Load District Summary
print(f"📂 '{DISTRICT_SUMMARY_FILE}', attempting to read...")
try:
    df_dist_summary = pd.read_csv(DISTRICT_SUMMARY_FILE, encoding='utf-8')
    print("✅ Read with UTF-8")
except UnicodeDecodeError:
    print("⚠️ UTF-8 failed, retrying with TIS-620...")
    df_dist_summary = pd.read_csv(DISTRICT_SUMMARY_FILE, encoding='tis-620')
    print("✅ Read with TIS-620")
cols_num = ['lat', 'lon', 'Total_Problems', 'Livability_Score_10', 'Avg_Price_Per_SqM']
for c in cols_num:
    if c in df_dist_summary.columns:
        if df_dist_summary[c].dtype == object:
            df_dist_summary[c] = df_dist_summary[c].astype(str).str.replace(',', '')
        df_dist_summary[c] = pd.to_numeric(df_dist_summary[c], errors='coerce')
print(f"✅ Loaded District Summary: {len(df_dist_summary)} rows")

@app.get("/")
def root():
    return {"message": "Urban Data API is running. Go to /docs to see endpoints."}

@app.get("/condo_data")
def get_condo_data(district: Optional[str] = None):
    # Get all Condos / Filter by District
    data = df_condo
    if not data.empty and district:
        data = data[data['district'] == district]
    return data.to_dict(orient="records")

# @app.get("/problem_data")
# def get_problem_data(limit: int = 20000):
#     # Get all Traffy Fondue
#     if df_problem.empty:
#         return []
#     # limit = 0 -> All
#     if limit == 0 or limit >= len(df_problem):
#         return df_problem.to_dict(orient="records")
#     return df_problem.sample(n=limit).to_dict(orient="records")

@app.get("/problem_summary")
def get_problem_summary():
    if df_prob_summary.empty:
        return []
    return df_prob_summary.to_dict(orient="records")

@app.get("/district_summary")
def get_district_summary():
    if df_dist_summary.empty:
        return []
    return df_dist_summary.to_dict(orient="records")