# streamlit_app.py
# run "streamlit run streamlit_app.py"
# stop Control (⌃) + C
import streamlit as st
import pandas as pd
import numpy as np
import folium 
from streamlit_folium import st_folium
import requests
import io # ใช้สำหรับกรณีที่ API ส่งไฟล์ CSV มาแทน JSON

from styles import CUSTOM_CSS
from data_loader import load_condo_data, load_problem_data
from views import visual_insights, future_prediction, data_overview
from viz_components import (
    create_single_layer_heatmap,
    create_bubble_chart,
    create_prediction_chart,
    create_problem_distribution_chart
)

# --- Page Configuration ---
st.set_page_config(
    page_title="The Prime Vibe or the Problem Drive?",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- CSS Injection ---
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Data Loading ---
with st.spinner('Connecting to the database...'):
    # Load data from API (via data_loader)
    df_condos = load_condo_data()   
    df_problems = load_problem_data()

# Fallback: If API fails, check if we can read CSV directly
if df_condos.empty:
    try:
        df_condos = pd.read_csv("mock_condos.csv")
        st.warning("⚠️ API connection failed. Using local 'mock_condos.csv' instead.")
    except:
        st.error("🚨 Failed to load data (API Down & No CSV found)")
        st.stop()

# Prepare Data
df_condos = df_condos.copy()
# Calculate center map
center_lat = df_condos['lat'].mean() if not df_condos.empty else 13.737778
center_lon = df_condos['lon'].mean() if not df_condos.empty else 100.5050

# --- Sidebar ---
with st.sidebar:
    st.title("Visualization Settings")
    st.markdown("---")

    page_selection = st.radio(
        "",
        ("Visual Insights", "Future Price Prediction", "Data Overview & Sources")
    )
    if page_selection == "Visual Insights":
        st.markdown("**Visual Insights**")
        st.caption("Section presents processed data through interactive visualizations.")
    elif page_selection == "Future Price Prediction":
        st.markdown("**Future Price Prediction**")
        st.caption("Simulate future property prices based on hypothetical reduction scenarios of specific urban problems.")
    elif page_selection == "Data Overview & Sources":
        st.markdown("**Data Overview & Sources**")
        st.caption("Review data sources and the project timeframe to verify the overall reliability of the data.")

    st.markdown("---")

# --- Main Panel ---
st.title("The Prime Vibe or the Problem Drive?")
st.subheader("Analyze the impact of city problems (Traffy Fondue) impact on property prices.")
st.markdown("---")

# --- Routing Logic ---
if page_selection == "Visual Insights":
    visual_insights.show(df_condos, center_lat, center_lon)

elif page_selection == "Future Price Prediction":
    future_prediction.show(df_condos)

elif page_selection == "Data Overview & Sources":
    data_overview.show(df_condos, df_problems)