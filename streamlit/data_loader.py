import pandas as pd
import requests
import streamlit as st
from typing import Optional

API_URL = "http://127.0.0.1:8000"

@st.cache_data(ttl=3600)  # Cache ข้อมูลไว้ 1 ชั่วโมงเพื่อลดการเรียก API ซ้ำๆ
def load_condo_data():
    """
    Fetch condo data from API Endpoint /condo_data
    """
    try:
        response = requests.get(f"{API_URL}/condo_data", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            
            # Convert date (string) -> datetime object
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
            return df
        else:
            st.error(f"❌ Error loading Condo Data: Status Code {response.status_code}")
            return pd.DataFrame()
            
    except requests.exceptions.ConnectionError:
        st.error("🚨 Failed to load data (API Down)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_problem_data():
    """
    Fetch Traffy Fondue from API Endpoint /problem_data
    """
    try:
        response = requests.get(f"{API_URL}/problem_data", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            st.error(f"❌ Error loading Problem Data: Status Code {response.status_code}")
            return pd.DataFrame()
            
    except requests.exceptions.ConnectionError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return pd.DataFrame()