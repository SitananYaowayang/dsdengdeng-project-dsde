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
    if not df_condos.empty:
        create_single_layer_heatmap(df_condos, center_lat, center_lon, layer_type=selected_layer)
    else:
        st.warning("Cannot display map: No data or lat/lon missing.")

    # --- 2. Bubble Chart ---
    st.header("Interactive Bubble Chart")
    if not df_condos.empty and 'year' in df_condos.columns:
        create_bubble_chart(df_condos)
    else:
        st.warning("Cannot display Bubble Chart: Data missing 'year' column or is empty.")
    st.markdown("---")

# --- Page 2: Future Price Prediction ---
elif page_selection == "Future Price Prediction":
    st.header("Future Price Prediction")
    st.caption("จำลองสถานการณ์ราคาคอนโดในอีก 5 ปีข้างหน้า หากปัญหาเมืองในพื้นที่ได้รับการแก้ไข")

    # --- 1. Select District ---
    district_list = sorted(df_condos['district'].unique().tolist())
    selected_district_pred = st.selectbox("🔍Select District:", district_list, index=0)

    # กรองข้อมูลเฉพาะเขตที่เลือก
    df_district = df_condos[df_condos['district'] == selected_district_pred]
    
    # คำนวณค่าปัจจุบัน
    if not df_district.empty:
        current_price = df_district['price_sqm'].mean()
        current_liva = df_district['livability_score'].mean()
    else:
        current_price = 0
        current_liva = 0

    # --- 2. Current Stats & Simulator Controls ---
    col_sim_1, col_sim_2 = st.columns([1, 3])

    with col_sim_1:
        st.subheader(f"📍 {selected_district_pred}")
        st.metric("ราคาเฉลี่ยปัจจุบัน (บาท/ตร.ม.)", f"฿{current_price:,.0f}")
        st.metric("คะแนนความน่าอยู่ (Livability)", f"{current_liva:.2f} / 10")
                
    with col_sim_2:
        st.subheader("เลือกปัญหาที่คาดว่าจะได้รับการแก้ไข")
        st.caption("การเลือกแก้ไขปัญหาจะช่วยเพิ่ม Growth Rate ของราคา")
        
        problem_options = ['ถนน', 'ทางเท้า', 'ความปลอดภัย', 'แสงสว่าง', 'ความสะอาด', 'กีดขวาง', 'ท่อระบายน้ำ', 'น้ำท่วม', 'ต้นไม้', 'PM2.5', 'จราจร', 'สะพาน']
        selected_fixes = []

        sub_cols = st.columns(3)
        for i, p in enumerate(problem_options):
            col_idx = i // 4 
            if col_idx < len(sub_cols):
                with sub_cols[col_idx]:
                    # เพิ่ม key เพื่อป้องกัน DuplicateWidgetID ถ้ามี checkbox ชื่อซ้ำกันในหน้าอื่น
                    if st.checkbox(f"{p}", value=False, key=f"chk_{p}"):
                        selected_fixes.append(p)

    # --- 3. Prediction Chart ---
    st.subheader("5-Year Price Prediction")
    st.caption("กราฟเส้นทำนายราคา 5 ปีข้างหน้า เปรียบเทียบระหว่าง Base Case (โตตามเงินเฟ้อปกติ) และ Improved Case (โตขึ้นหากแก้ปัญหาเมืองที่เลือก)")
    if current_price > 0:
        create_prediction_chart(current_price, selected_fixes)
    else:
        st.error("ไม่พบข้อมูลราคาในเขตนี้")

    st.markdown("---")

elif page_selection == "Data Overview & Sources":
    st.header("Data Overview & Sources")

    # --- 1. Top Level Metrics ---
    st.subheader("Top Level Metrics")
    col_ov_1, col_ov_2, col_ov_3 = st.columns(3)
    
    with col_ov_1:
        total_problems = len(df_problems) if not df_problems.empty else 0
        st.metric("Total Reported Issues", f"{total_problems:,}")
        st.markdown(
        """
        Source: [TraffyFondue](https://bangkok.traffy.in.th/)
        """,
        unsafe_allow_html=False
        )
    
    with col_ov_2:
        total_projects = len(df_condos)
        st.metric("Total Condo Projects", f"{total_projects:,}")
        st.markdown(
        """
        Source: [LivingInsider](https://www.livinginsider.com/)
        """,
        unsafe_allow_html=False
        )
        
    with col_ov_3:
        avg_price_all = df_condos['price_sqm'].mean() if not df_condos.empty else 0
        st.metric("City-wide Avg Price", f"฿{avg_price_all:,.0f}")

    st.markdown("---")

    # --- 2. Problem Distribution Chart ---
    st.subheader("Reported Issue Distribution")

    if not df_problems.empty:
        create_problem_distribution_chart(df_problems)
    else:
        st.info("No problem data loaded.")

    st.markdown("---")

    # --- 3. Sample Raw Data ---
    # st.subheader("Sample Raw Data")
    # tab1, tab2 = st.tabs(["Condos", "Problems"])
        
    # with tab1:
    #     st.dataframe(df_condos[['project_name', 'district', 'price_sqm']].head(10), use_container_width=True)
        
    # with tab2:
    #     if not df_problems.empty:
    #         st.dataframe(df_problems[['ticket_id', 'type', 'district', 'status']].head(10), use_container_width=True)
    #     else:
    #         st.write("No data.")

    # st.markdown("---")