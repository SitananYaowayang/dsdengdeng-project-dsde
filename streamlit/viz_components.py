# viz_functions.py

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px

# Heatmap (Layer 1)
def create_price_heatmap(df: pd.DataFrame, center_lat: float, center_lon: float):
    st.subheader("🔥 Layer 1: Price Heatmap (Price per Square Meter)")
    
    # ใช้น้ำหนัก (Weight) เป็นราคาต่อ ตร.ม.
    price_data = [[row.lat, row.lon, row.price_sqm] for idx, row in df.iterrows()]
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodbpositron")
    
    # HeatMap: ใช้ Price/sqm เป็น Weight
    HeatMap(price_data, name='Price Heatmap', radius=15).add_to(m)

    st_folium(m, width=700, height=450, key="price_map")

# Heatmap (Layer 2)
def create_problem_heatmap(df: pd.DataFrame, center_lat: float, center_lon: float):
    st.subheader("🚨 Layer 2: Problem Intensity (ความรุนแรงของปัญหา)")
    
    # ใช้น้ำหนัก (Weight) เป็นจำนวนปัญหา x Angry Score
    problem_intensity_data = [
        [row.lat, row.lon, row.problem_count_500m * row.angry_score] 
        for idx, row in df.iterrows()
    ]
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodbdarkmatter")

    # HeatMap: ใช้ Problem Count * Angry Score เป็น Weight
    HeatMap(problem_intensity_data, name='Problem Intensity', radius=15, 
            gradient={0.4: 'blue', 0.65: 'orange', 1: 'red'}).add_to(m)

    st_folium(m, width=700, height=450, key="problem_map")

# Bar Chart แสดง Feature Importance จาก Regression Model
def create_feature_importance_chart():
    st.subheader("📊 Model Feature Importance")
    st.markdown("แสดงปัจจัยที่มีผลต่อราคาต่อ ตร.ม. (จาก XGBoost Model)")
    
    importance_data = pd.DataFrame({
        'Feature': ['Angry Score (500m)', 'Distance to BTS/MRT', 'Problem Count (500m)', 'Project Age', 'Commercial Area Proximity'],
        'Importance Score': [0.45, 0.30, 0.15, 0.07, 0.03]
    }).sort_values('Importance Score', ascending=True)

    fig = px.bar(
        importance_data,
        x='Importance Score',
        y='Feature',
        orientation='h',
        title='Top 5 Drivers of Price per Square Meter',
        color='Importance Score',
        color_continuous_scale=px.colors.sequential.Sunset
    )
    st.plotly_chart(fig, use_container_width=True)
    
# Quadrant Analysis: Livability Score (X) vs Price/sqm (Y)
def create_quadrant_analysis(df: pd.DataFrame):
    st.subheader("📈 Quadrant Analysis: Price (Y) vs. Livability Score (X)")
    st.markdown("ค้นหา 'Gold Mine' (Undervalued) ใน Quadrant ล่างซ้าย (ปัญหาน้อย, ราคาถูก)")
    
    # ใช้ Valuation Status ที่คำนวณในฟังก์ชันก่อนหน้า
    if 'valuation_status' not in df.columns:
        df['valuation_status'] = pd.cut(
            df['livability_score'] / df['price_sqm'],
            bins=[0, 0.00003, 0.00005, 1],
            labels=['Undervalued 🟢', 'Fairly Valued 🟡', 'Overpriced 🔴']
        )
    
    fig = px.scatter(
        df, 
        x='livability_score', 
        y='price_sqm', 
        color='valuation_status',
        hover_data=['project_name', 'problem_count_500m'],
        color_discrete_map={'Undervalued 🟢': 'green', 'Fairly Valued 🟡': 'orange', 'Overpriced 🔴': 'red'},
        labels={
             'livability_score': 'Livability Score (ต่ำ = น่าอยู่/ปัญหาน้อย)',
             'price_sqm': 'ราคาต่อ ตร.ม. (บาท)'
        },
        title='Property Valuation by Livability & Price'
    )
    
    # เพิ่มเส้นแบ่ง Quadrant (Mock: ค่าเฉลี่ย)
    avg_score = df['livability_score'].mean()
    avg_price = df['price_sqm'].mean()
    
    fig.add_vline(x=avg_score, line_width=1, line_dash="dash", line_color="grey")
    fig.add_hline(y=avg_price, line_width=1, line_dash="dash", line_color="grey")
    
    st.plotly_chart(fig, use_container_width=True)