# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import folium 
from streamlit_folium import st_folium


from viz_components import (
    create_price_heatmap, 
    create_problem_heatmap,
    create_livability_heatmap,
    create_single_layer_heatmap,
    create_feature_importance_chart,
    create_quadrant_analysis
)

# --- Page Configuration ---
st.set_page_config(
    page_title="The Prime Vibe or the Problem Drive?",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- CSS Injection ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai+Looped:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');
    
    html, body, [class*="st-"] {
        font-family: 'IBM Plex Sans Thai Looped', sans-serif !important;
    }
    
    /* Force all icon SPAN elements to use the correct Material Symbols font */
    span[data-testid="stIconMaterial"],
    [data-testid*="stIcon"] *,
    i, 
    button[title*="navigation"] *
    { 
        font-family: "Material Symbols Outlined", sans-serif !important;
    }
    
    /* Ensure the hamburger icon (if visible) is also fixed */
    .st-emotion-cache-1mnn934 * {
        font-family: "Material Symbols Outlined", sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Mock Data (โหลดจาก CSV) ---
@st.cache_data
def load_data(csv_path="mock.csv"):
    """
    Load main data from CSV (call only once)
    CSV ต้องมีคอลัมน์: 
    ['project_name', 'district', 'lat', 'lon', 'price_sqm', 'problem_count_500m', 'angry_score', 'livability_score']
    """
    df = pd.read_csv(csv_path)

    # กำหนด center map แบบเฉลี่ยพิกัดทั้งหมด
    center_lat = df['lat'].mean()
    center_lon = df['lon'].mean()

    return df, center_lat, center_lon

# Load data
df_mock, center_lat, center_lon = load_data("mock.csv")

# --- Sidebar ---
with st.sidebar:
    st.title("Visualization Settings")
    st.markdown("---")

    page_selection = st.radio(
        "",
        ("Visual Insights", "Data Overview & Sources")
    )

    if page_selection == "Visual Insights":
        st.markdown("**Visual Insights**")
        st.caption("Section presents processed data through interactive visualizations.")
    elif page_selection == "Data Overview & Sources":
        st.markdown("**Data Overview & Sources**")
        st.caption("Review data sources and the project timeframe to verify the overall reliability of the data.")

    st.markdown("---")
    
    # ตัวกรองรวม (ใช้ได้ทั้ง 2 หน้า)
    st.header("Global Filters")
    selected_district = st.multiselect(
        "เลือกเขตที่สนใจ:", 
        options=df_mock['district'].unique().tolist(), 
        default=df_mock['district'].unique().tolist()
    )
    min_price, max_price = st.slider(
        "ช่วงราคาต่อ ตร.ม. (บาท):",
        min_value=80000,
        max_value=250000,
        value=(100000, 200000),
        step=5000
    )

# Filter data (maidai ใช้)
df_filtered = df_mock[
    (df_mock['district'].isin(selected_district)) &
    (df_mock['price_sqm'] >= min_price) &
    (df_mock['price_sqm'] <= max_price)
]

# ------------------
# --- Main Panel ---
# ------------------
st.title("The Prime Vibe or the Problem Drive?")
st.subheader("Analyze the impact of city problems (Traffy Fondue) impact on property prices.")
st.markdown("---")

# --- Page 1: Visual Insights ---
if page_selection == "Visual Insights":
    
    # --- 1. Heatmap ---
    st.header("Heatmap")
    # st.markdown("เปรียบเทียบความร้อนของราคาอสังหาฯ (Layer 1) และความรุนแรงของปัญหาเมือง (Layer 2)")

    # Filters
    with st.expander("⚙️ ตัวกรองสำหรับแผนที่"):
        col_map_filter_1, col_map_filter_2 = st.columns(2)
        with col_map_filter_1:
            st.multiselect("เน้นปัญหาเมือง:", options=['ขยะ', 'ทางเท้า', 'น้ำท่วม'], default=['ขยะ'])
        with col_map_filter_2:
            st.slider("ช่วงราคา (ต่อ ตร.ม.):", 50000, 300000)
    # เลือก layer ใน expander
        layer_option = st.radio(
            "เลือก Heatmap Layer:",
            ["Condominium Pricing (Price per Square Meter)", 
            "Community Challenges (Problem Intensity)", 
            "Overall Livability Score (คะแนนความน่าอยู่โดยรวม)"]
        )

    # แปลงตัวเลือกให้ตรงกับ function
    layer_map = {
        "Condominium Pricing (Price per Square Meter)": "price",
        "Community Challenges (Problem Intensity)": "problem",
        "Overall Livability Score (คะแนนความน่าอยู่โดยรวม)": "livability"
    }
    selected_layer = layer_map[layer_option]

    # แสดง map
    create_single_layer_heatmap(df_mock, center_lat, center_lon, layer_type=selected_layer)

    # --- 2. Selectbox & KPIs ---
    district_options = df_mock['district'].unique().tolist()
    district_options.insert(0, 'ทั้งหมด (All Districts)')

    selected_district = st.selectbox(
        "Select District:",
        options=district_options
    )

    if selected_district == 'ทั้งหมด (All Districts)':
        df_filtered = df_mock.copy()
    else:
        df_filtered = df_mock[df_mock['district'] == selected_district].copy()

    # Key Performance Indicators (KPIs)
    st.header("Key Performance Indicators (KPIs) & Predictive ROI")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="ค่าเฉลี่ย Livability Score (ต่ำสุด 3.0)", value=f"{df_filtered['livability_score'].mean():.2f}")
    with col2:
        st.metric(label="ราคาเฉลี่ยต่อ ตร.ม. (บาท)", value=f"฿{df_filtered['price_sqm'].mean():,.0f}")
    with col3:
        # ผลลัพธ์จากการทำนายของ Model (Mock)
        # ตัวอย่าง: การลดปัญหาทางเท้า 10% เพิ่มราคาคอนโด 12.5% 
        st.metric(
            label="Predictive Price Uplift (ROI)", 
            value="12.5%", 
            delta="ถ้าลดปัญหาทางเท้า 10%"
        )

    st.markdown("---")

# --- Page 2: Model Insights & Ranking ---
elif page_selection == "Data Overview & Sources":
    
    # --- 1. Data Overview ---
    col_data_1, col_data_2, col_data_3 = st.columns(3)

    with col_data_1:
        st.metric(label="Total Reported Issues", value="187,854") 
        st.caption("From Traffy Fondue")
    with col_data_2:
        st.metric(label="Total Price Samples", value="25,151")
        st.caption("From LivingInsider / DDproperty")
    with col_data_3:
        st.metric(label="Data Period", value="2022 - 2025")
        st.caption("Historical Data Range")

    st.markdown("---")

    # --- 2. Reported Issues Distribution ---

    # --- 3. Model Feature Importance ---
    create_feature_importance_chart()
    st.markdown("---")
    
    # --- 4. Quadrant Analysis (Scatter Plot) ---
    create_quadrant_analysis(df_filtered)
    st.markdown("---")
    
    # --- 5. Undervalued Ranking Table ---
    st.header("Investment Ranking: Undervalued Projects")
    
    # ต้องคำนวณ 'valuation_status' ก่อนเพื่อให้ตารางแสดงผลได้
    # Logic นี้ถูกทำซ้ำจาก viz_functions เพื่อให้แน่ใจว่า Column มีอยู่
    df_filtered['valuation_status'] = pd.cut(
        df_filtered['livability_score'] / df_filtered['price_sqm'],
        bins=[0, 0.00003, 0.00005, 1],
        labels=['Undervalued 🟢', 'Fairly Valued 🟡', 'Overpriced 🔴']
    )
    
    df_undervalued = df_filtered[df_filtered['valuation_status'] == 'Undervalued 🟢'].sort_values(
        'price_sqm', ascending=True
    )[['project_name', 'district', 'price_sqm', 'livability_score', 'problem_count_500m']]
    
    st.dataframe(
        df_undervalued.head(10).rename(columns={
            'project_name': 'โครงการ', 
            'district': 'ย่าน', 
            'price_sqm': 'ราคา/ตร.ม. (บาท)',
            'livability_score': 'Score (น่าอยู่)',
            'problem_count_500m': 'ปัญหา/500m'
        }), 
        hide_index=True, 
        use_container_width=True
    )