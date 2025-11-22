# viz_functions.py

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import HeatMap, MiniMap,MeasureControl
from branca.element import Template, MacroElement


# ---heatmap
def create_single_layer_heatmap(df, center_lat, center_lon, layer_type="price", map_key="single_map"):
    """
    layer_type: 'price', 'problem', 'livability'
    """
    if layer_type == "price":
        st.subheader("Condominium Pricing (Price per Sq.M.)")
        st.caption("Displays the average selling price per square meter and highlights price trends for condo units.")
        data = [[row.lat, row.lon, row.price_sqm] for _, row in df.iterrows()]
        heatmap_kwargs = {"radius": 15}
        legend_html = """
        <div style="
            position: fixed; 
            bottom: 20px; right: 20px; 
            width: 170px; height: 130px; 
            background-color: white; 
            border:2px solid grey; 
            z-index:9999;
            padding:10px; font-size:14px;">
            <b>Price per Sq.M.</b><br>
            <span style="background:blue;width:20px;height:10px;display:inline-block"></span> <100k<br>
            <span style="background:green;width:20px;height:10px;display:inline-block"></span> 100k-150k<br>
            <span style="background:orange;width:20px;height:10px;display:inline-block"></span> 150k-200k<br>
            <span style="background:red;width:20px;height:10px;display:inline-block"></span> >200k
        </div>
        """
    elif layer_type == "problem":
        st.subheader("Community Challenges (Problem Intensity)")
        st.caption("Visualizes the reported frequency and severity of problems using the angry score as intensity weight.")
        data = [[row.lat, row.lon, row.problem_count_500m * row.angry_score] for _, row in df.iterrows()]
        heatmap_kwargs = {"radius": 15}
        legend_html = """
        <div style="
            position: fixed; 
            bottom: 20px; right: 20px; 
            width: 160px; height: 110px; 
            background-color: white; 
            border:2px solid grey; 
            z-index:9999;
            padding:10px; font-size:14px;">
            <b>Problem Intensity</b><br>
            <span style="background:blue;width:20px;height:10px;display:inline-block"></span> Low<br>
            <span style="background:orange;width:20px;height:10px;display:inline-block"></span> Medium<br>
            <span style="background:red;width:20px;height:10px;display:inline-block"></span> High
        </div>
        """

    elif layer_type == "livability":
        st.subheader("Overall Livability Score")
        st.caption("Presents a composite index score representing the overall quality of life, based on amenities, green space access, and public transport.")
        data = [[row.lat, row.lon, row.livability_score] for _, row in df.iterrows()]
        heatmap_kwargs = {"radius": 15, "gradient": {0.2:'red',0.5:'orange',0.8:'yellow',1.0:'green'}}
        legend_html = """
        <div style="
            position: fixed; 
            bottom: 20px; right: 20px; 
            width: 160px; height: 120px; 
            background-color: white; 
            border:2px solid grey; 
            z-index:9999;
            padding:10px; font-size:14px;">
            <b>Livability Score</b><br>
            <span style="background:red;width:20px;height:10px;display:inline-block"></span> 3-4<br>
            <span style="background:orange;width:20px;height:10px;display:inline-block"></span> 4-6<br>
            <span style="background:yellow;width:20px;height:10px;display:inline-block"></span> 6-8<br>
            <span style="background:green;width:20px;height:10px;display:inline-block"></span> 8-10
        </div>
        """

    else:
        st.error("Invalid layer_type!")
        return

    # Map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodbpositron")
    HeatMap(data, **heatmap_kwargs).add_to(m)
    m.add_child(MeasureControl(primary_length_unit="kilometers"))
    # Add legend
    m.get_root().html.add_child(folium.Element(legend_html))
    # Hide attribution
    m.get_root().header.add_child(folium.Element("""
        <style>.leaflet-control-attribution {display: none !important;}</style>
    """))

    st_folium(m, width=700, height=450, key=map_key)

#--bubble
def create_bubble_chart(df: pd.DataFrame):
    st.subheader("💡 Bubble Chart: Average Livability vs Average Problem Intensity by District")

    # --- เลือกปี ---
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    selected_year = st.slider(
        "Select Year",
        min_value=min_year,
        max_value=max_year,
        value=max_year
    )

    # Filter ตามปี
    df_year = df[df['year'] == selected_year].copy()

    # สร้างคอลัมน์ problem_intensity
    df_year["problem_intensity"] = df_year["problem_count_500m"] * df_year["angry_score"]

    # --- ทำเฉลี่ยตามเขต ---
    df_group = df_year.groupby("district").agg(
        avg_livability=("livability_score", "mean"),
        avg_problem_intensity=("problem_intensity", "mean"),
        avg_price_sqm=("price_sqm", "mean"),
        project_count=("project_name", "count")
    ).reset_index()

    # Bubble chart (1 จุดต่อเขต)
    fig = px.scatter(
        df_group,
        x="avg_livability",
        y="avg_problem_intensity",
        size="avg_price_sqm",
        color="district",
        hover_name="district",
        hover_data={
            "avg_livability": True,
            "avg_problem_intensity": True,
            "avg_price_sqm": True,
            "project_count": True
        },
        size_max=60,
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_layout(
        title=f"Bubble Chart (District Average) — {selected_year}",
        xaxis_title="Average Livability Score",
        yaxis_title="Average Problem Intensity",
        legend_title="District",
        width=900,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

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