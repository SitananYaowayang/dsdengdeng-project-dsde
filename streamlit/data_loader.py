import pandas as pd
import requests
import streamlit as st
from typing import Optional
from model.prediction_service import CondoPricePredictor

API_URL = "http://127.0.0.1:8000"

@st.cache_resource
def load_model():
    return CondoPricePredictor()
try:
    AI = load_model()
    district_list = list(AI.df_scores.index.unique())
    district_list.sort()     
except Exception as e:
    st.error(f"An error occurred while loading the model data: {e}")
    st.stop()

@st.cache_data(ttl=3600) # Cache 1 hr
def load_data():
    df_condo = _fetch_condo_data()
    df_problems = _fetch_problem_data()
    df_problem_summary = _fetch_problem_summary_data()
    df_district_summary = _fetch_district_summary_data()
    return df_condo, df_problems, df_problem_summary, df_district_summary

@st.cache_data(ttl=3600)
def _fetch_condo_data():
    try:
        response = requests.get(f"{API_URL}/condo_data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(response.json())
            # Convert numeric columns explicitly
            cols_num = ['lat', 'lon', 'price_per_sqm', 'usable_area', 'bedroom', 'restroom']
            for c in cols_num:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
            return df
        else:
            st.error(f"❌ Error loading Condo Data: Status Code {response.status_code}")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("🚨 Failed to load data (API Down)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Connect API Error (Condo): {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def _fetch_problem_data():
    """
    Fetch ALL Traffy Fondue data (100k rows)
    """
    try:
        with st.spinner('Retrieving 100,000 items...'):
            response = requests.get(f"{API_URL}/problem_data", params={"limit": 0}, timeout=120)
        
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if df.empty:
                return df
            
            # --- PREPROCESSING FOR VISUALIZATION ---
            # 1. Ensure Lat/Lon are numeric
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna(subset=['lat', 'lon']) # Remove invalid coords
            return df
        else:
            st.error(f"❌ Error loading Problem Data: Status Code {response.status_code}")
            return pd.DataFrame()
    except requests.exceptions.ReadTimeout:
        st.error("⏰ Time out")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("🚨 Failed to load data (API Down)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Connect API Error (Problem): {e}")
        return pd.DataFrame()
    
@st.cache_data(ttl=3600)
def _fetch_district_summary_data():
    try:
        response = requests.get(f"{API_URL}/district_summary", timeout=10)
        
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if df.empty:
                return df
            
            cols_num = ['lat', 'lon', 'Total_Listings', 'Total_Problems', 'Livability_Score_10', 'Avg_Price', 'Avg_Price_Per_SqM', 'Avg_Size', 'Avg_Severity']
            for c in cols_num:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
            
            return df
        else:
            st.error(f"❌ Error loading District Summary: Status Code {response.status_code}")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        print("🚨 Failed to load district summary (API Down)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Connect API Error (District Summary): {e}")
        return pd.DataFrame()
    
@st.cache_data(ttl=3600)
def _fetch_problem_summary_data():
    try:
        response = requests.get(f"{API_URL}/problem_summary", timeout=10)
        
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if df.empty:
                return df
            
            cols_num = ['Total_Count']
            for c in cols_num:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
            
            return df
        else:
            st.error(f"❌ Error loading Problem Summary: Status Code {response.status_code}")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        print("🚨 Failed to load problem summary (API Down)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Connect API Error (Problem Summary): {e}")
        return pd.DataFrame()