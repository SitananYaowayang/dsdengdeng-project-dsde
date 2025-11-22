# streamlit_app.py
# run "streamlit run streamlit_app.py"
# stop Control (⌃) + C
import streamlit as st
import pandas as pd
import numpy as np
import folium 
from streamlit_folium import st_folium
# 🟢 เพิ่มการนำเข้า requests
import requests
import io # ใช้สำหรับกรณีที่ API ส่งไฟล์ CSV มาแทน JSON


from viz_components import (
    create_single_layer_heatmap,
    create_bubble_chart,
    create_feature_importance_chart,
    create_quadrant_analysis
)

# --- Page Configuration และ CSS Injection (คงเดิม) ---
st.set_page_config(
    page_title="The Prime Vibe or the Problem Drive?",
    layout="wide", 
    initial_sidebar_state="expanded"
)

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


# --- Data Loading ---
@st.cache_data
def load_data(api_url: str):
    """
    Load main data from an external API endpoint.
    Assumes the API returns a JSON array of records.
    """
    st.info(f"Attempting to fetch data from API: {api_url}")
    
    try:
        # ดึงข้อมูลจาก API
        response = requests.get(api_url, timeout=15)
        response.raise_for_status() # ตรวจสอบข้อผิดพลาด HTTP (4xx, 5xx)
        
        # แปลงข้อมูล JSON ที่ได้รับกลับมาเป็น Pandas DataFrame
        data = response.json()
        df = pd.DataFrame.from_records(data)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API. Please check the URL and network connection: {e}")
        # กำหนดค่าเริ่มต้นและ return DataFrame ว่างหากเกิดข้อผิดพลาด
        df = pd.DataFrame() 
        center_lat = 13.737778 # Default Bangkok Center
        center_lon = 100.5050
        return df, center_lat, center_lon

    # 🟢 ตรวจสอบข้อมูลก่อนคำนวณ center
    if df.empty or 'lat' not in df.columns or 'lon' not in df.columns:
        st.error("API returned no data or missing essential columns ('lat', 'lon').")
        center_lat = 13.737778
        center_lon = 100.5050
    else:
        # ทำความสะอาดและคำนวณ center map
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df.dropna(subset=['lat', 'lon'], inplace=True)
        
        center_lat = df['lat'].mean()
        center_lon = df['lon'].mean()

    return df, center_lat, center_lon

# 🟢 กำหนด API Endpoint และเรียกใช้
API_ENDPOINT = "http://localhost:8000/condo_data"
df_mock, center_lat, center_lon = load_data(API_ENDPOINT)

# 🟢 เพิ่มการตรวจสอบเพื่อให้แอปหยุดทำงานหากดึงข้อมูลล้มเหลว
if df_mock.empty:
    st.stop()


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
    # ตรวจสอบว่า df_mock มีข้อมูลก่อนใช้ .unique()
    if not df_mock.empty and 'district' in df_mock.columns:
        district_options = df_mock['district'].unique().tolist()
    else:
        district_options = []

    selected_district = st.multiselect(
        "เลือกเขตที่สนใจ:", 
        options=district_options, 
        default=district_options
    )
    min_price, max_price = st.slider(
        "ช่วงราคาต่อ ตร.ม. (บาท):",
        min_value=80000,
        max_value=250000,
        value=(100000, 200000),
        step=5000
    )
    
    st.markdown("---")


# Filter data (maidai ใช้)
if not df_mock.empty:
    df_filtered = df_mock[
        (df_mock['district'].isin(selected_district)) &
        (df_mock['price_sqm'] >= min_price) &
        (df_mock['price_sqm'] <= max_price)
    ]
else:
    df_filtered = pd.DataFrame() # ใช้ DataFrame ว่างถ้าไม่มีข้อมูล

# ... (โค้ด Main Panel) ...
st.title("The Prime Vibe or the Problem Drive?")
st.subheader("Analyze the impact of city problems (Traffy Fondue) impact on property prices.")
st.markdown("---")

# --- Page 1: Visual Insights ---
if page_selection == "Visual Insights":
    
    # --- 1. Heatmap ---
    st.header("Heatmap")
    
    with st.expander("⚙️ ตัวกรองสำหรับแผนที่"):
        col_map_filter_1, col_map_filter_2 = st.columns(2)
        with col_map_filter_1:
            st.multiselect("เน้นปัญหาเมือง:", options=['ขยะ', 'ทางเท้า', 'น้ำท่วม'], default=['ขยะ'])
        with col_map_filter_2:
            st.slider("ช่วงราคา (ต่อ ตร.ม.):", 50000, 300000)
    
        layer_option = st.radio(
            "เลือก Heatmap Layer:",
            ["Condominium Pricing (Price per Square Meter)", 
            "Community Challenges (Problem Intensity)", 
            "Overall Livability Score (คะแนนความน่าอยู่โดยรวม)"]
        )

    layer_map = {
        "Condominium Pricing (Price per Square Meter)": "price",
        "Community Challenges (Problem Intensity)": "problem",
        "Overall Livability Score (คะแนนความน่าอยู่โดยรวม)": "livability"
    }
    selected_layer = layer_map[layer_option]

    # แสดง map
    if not df_mock.empty:
        create_single_layer_heatmap(df_mock, center_lat, center_lon, layer_type=selected_layer)
    else:
        st.warning("Cannot display map: No data or lat/lon missing.")

    # --- 2. Selectbox & KPIs ---
    district_options = df_mock['district'].unique().tolist() if 'district' in df_mock.columns and not df_mock.empty else []
    district_options.insert(0, 'ทั้งหมด (All Districts)')

    selected_district_kpi = st.selectbox(
        "Select District:",
        options=district_options
    )

    if selected_district_kpi == 'ทั้งหมด (All Districts)':
        df_kpi_filtered = df_mock.copy()
    elif not df_mock.empty and 'district' in df_mock.columns:
        df_kpi_filtered = df_mock[df_mock['district'] == selected_district_kpi].copy()
    else:
        df_kpi_filtered = pd.DataFrame()


    # Key Performance Indicators (KPIs)
    st.header("Key Performance Indicators (KPIs) & Predictive ROI")
    col1, col2, col3 = st.columns(3)
    if not df_kpi_filtered.empty and 'livability_score' in df_kpi_filtered.columns and 'price_sqm' in df_kpi_filtered.columns:
        with col1:
            st.metric(label="ค่าเฉลี่ย Livability Score (ต่ำสุด 3.0)", value=f"{df_kpi_filtered['livability_score'].mean():.2f}")
        with col2:
            st.metric(label="ราคาเฉลี่ยต่อ ตร.ม. (บาท)", value=f"฿{df_kpi_filtered['price_sqm'].mean():,.0f}")
    else:
        with col1:
            st.metric(label="ค่าเฉลี่ย Livability Score (ต่ำสุด 3.0)", value="N/A")
        with col2:
            st.metric(label="ราคาเฉลี่ยต่อ ตร.ม. (บาท)", value="N/A")
            
    with col3:
        st.metric(
            label="Predictive Price Uplift (ROI)", 
            value="12.5%", 
            delta="ถ้าลดปัญหาทางเท้า 10%"
        )

    st.markdown("---")

    # --- 3. Bubble Chart ---
    st.header("Interactive Bubble Chart")
    if not df_mock.empty and 'year' in df_mock.columns:
        create_bubble_chart(df_mock)
    else:
        st.warning("Cannot display Bubble Chart: Data missing 'year' column or is empty.")
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

    # --- 2. Reported Issues Distribution (No code provided for this section) ---

    # --- 3. Model Feature Importance ---
    create_feature_importance_chart()
    st.markdown("---")
    
    # --- 4. Quadrant Analysis (Scatter Plot) ---
    if not df_filtered.empty:
        create_quadrant_analysis(df_filtered)
    else:
        st.warning("Cannot display Quadrant Analysis: Filtered data is empty.")
    st.markdown("---")
    
    # --- 5. Undervalued Ranking Table ---
    st.header("Investment Ranking: Undervalued Projects")
    
    if not df_filtered.empty and all(col in df_filtered.columns for col in ['livability_score', 'price_sqm']):
        # ต้องคำนวณ 'valuation_status' ก่อนเพื่อให้ตารางแสดงผลได้
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
    else:
        st.warning("Cannot generate ranking: Filtered data is empty or missing required columns.")