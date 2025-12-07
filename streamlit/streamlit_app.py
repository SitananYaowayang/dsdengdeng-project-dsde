# streamlit_app.py
# run "streamlit run streamlit_app.py"
# stop Control (⌃) + C
import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

from styles import CUSTOM_CSS
from data_loader import _fetch_condo_data, _fetch_problem_data, _fetch_problem_summary_data, _fetch_district_summary_data
from views import visual_insights, data_overview, price_forecasting

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
    df_condos = _fetch_condo_data()   
    df_problems = _fetch_problem_data()
    df_problem_summary = _fetch_problem_summary_data()
    df_district_summary = _fetch_district_summary_data()

# Fallback: If API fails, check if we can read CSV directly
if df_condos.empty | df_problems.empty:
    try:
        st.warning("⚠️ API connection failed")
    except:
        st.error("🚨 Failed to load data (API Down & No CSV found)")
        st.stop()

# --- Sidebar ---
with st.sidebar:
    st.title("Visualization Settings")
    st.markdown("---")

    page_selection = st.radio(
        "",
        ("Visual Insights", "Price Forecasting", "Data Overview & Sources")
    )
    if page_selection == "Visual Insights":
        st.markdown("**Visual Insights**")
        st.caption("Section presents processed data through interactive visualizations.")
    elif page_selection == "Price Forecasting":
        st.markdown("**Price Forecasting**")
        st.caption("Estimate condominium market price based on district, room layout and size.")
    elif page_selection == "Data Overview & Sources":
        st.markdown("**Data Overview & Sources**")
        st.caption("Review data sources and the project timeframe to verify the overall reliability of the data.")

    st.markdown("---")

    st.markdown("""
        <div style='position: fixed; bottom: 20px; left: 20px; font-size: 12px; opacity: 0.7;'>
            © 2025 Dsdengdeng Project<br>
            Data Source: Traffy Fondue, DDProperty, Open Data BKK
        </div>
    """, unsafe_allow_html=True)

# --- Main Panel ---
st.title("The Prime Vibe or the Problem Drive?")
st.subheader("Analyze the impact of city problems (Traffy Fondue) impact on property prices.")
st.markdown("---")

# --- Routing Logic ---
if page_selection == "Visual Insights":
    visual_insights.show(df_condos, df_problems, df_district_summary)

elif page_selection == "Price Forecasting":
    price_forecasting.show(df_condos)

elif page_selection == "Data Overview & Sources":
    data_overview.show(df_condos, df_problem_summary, df_district_summary)