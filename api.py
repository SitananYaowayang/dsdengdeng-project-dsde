# run "python -m uvicorn api:app"
# port 8000
# stop Control (⌃) + C
from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.get("/condo_data")
def get_condo_data():
    df = pd.read_csv("mock2.csv")
    return df.to_dict(orient="records")
