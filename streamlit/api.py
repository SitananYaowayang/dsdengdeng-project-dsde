# run "python -m uvicorn api:app"
# port 8000
# stop Control (⌃) + C
import pandas as pd
from fastapi import FastAPI
from typing import Optional
import uvicorn

app = FastAPI()

# Read mock data from local storage
try:
    df_condos = pd.read_csv("mock_condos.csv")
    df_problems = pd.read_csv("mock_problems.csv")
except FileNotFoundError:
    print("Please run mock_gen.py first to generate CSV files.")
    df_condos = pd.DataFrame()
    df_problems = pd.DataFrame()

@app.get("/")
def root():
    return {"message": "Urban Data API is running. Go to /docs to see endpoints."}

@app.get("/condo_data")
def get_condo_data(district: Optional[str] = None):
    """
    Get all Condos / Filter by District
    """
    data = df_condos
    if district:
        data = data[data['district'] == district]
    
    return data.fillna("").to_dict(orient="records")

@app.get("/problem_data")
def get_problem_data():
    """
    Get all Traffy Fondue
    """
    data = df_problems
    return data.fillna("").to_dict(orient="records")