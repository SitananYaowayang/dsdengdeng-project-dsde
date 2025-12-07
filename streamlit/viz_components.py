# viz_functions.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import HeatMap, MiniMap, MeasureControl
from branca.element import Template, MacroElement
import math

# ---heatmap
def create_single_layer_heatmap(df, layer_type="price"):
    """
    layer_type: 'price', 'problem', 'livability'
    สร้าง Heatmap โดยใช้ PyDeck และ st.pydeck_chart
    """
    
    if df.empty:
        st.warning("Data is empty. Cannot draw map.")
        return

    # 1. คำนวณหาจุดศูนย์กลางของแผนที่ (View State)
    # ใช้ค่าเฉลี่ยของ lat/lon เป็นจุดศูนย์กลาง
    center_lat = df['lat'].mean()
    center_lon = df['lon'].mean()
    
    # 2. เตรียมข้อมูลและตั้งค่า PyDeck Layer ตาม Layer Type
    # กำหนด View State เริ่มต้น
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=9.5,
        pitch=0,
    )
    
    # ตัวแปรสำหรับ PyDeck Layer
    layer = None
    tooltip_data = None
    
    if layer_type == "price":
        st.subheader("Condominium Pricing (Price per Sq.M.)")
        st.caption("Displays the average selling price per square meter and highlights price trends for condo units.")

        df['weight_value'] = df['Avg_Price']
        weight_column = 'weight_value'
        df['Avg_Price'] = pd.to_numeric(df['Avg_Price'], errors='coerce')

        # Drop invalid values (<=0 or NaN)
        df = df[df['Avg_Price'] > 0].dropna(subset=['Avg_Price'])

        p_min = df['Avg_Price'].min()
        p_max = df['Avg_Price'].max()

        # หาความใหญ่ของเลข เพื่อให้ปัดเป็นหลักพัน
        order = 10 ** (int(np.log10(p_min)) - 1)

        rounded_min = np.floor(p_min / order) * order
        rounded_max = np.ceil(p_max / order) * order

        selected_range = st.slider(
            "ช่วงราคา (บาท ต่อ ตร.ม.):",
            min_value=float(rounded_min),
            max_value=float(rounded_max),
            value=(
                float(df['Avg_Price'].quantile(0.2)),
                float(df['Avg_Price'].quantile(0.7))
            ),
            step=float(order),
        )
        df_filtered = df[
            (df['Avg_Price'] >= selected_range[0]) &
            (df['Avg_Price'] <= selected_range[1])
        ].copy()

        if df_filtered.empty:
            st.warning("No data found within the selected range 🙅‍♀️")
            return
        
        # PyDeck Heatmap Layer
        layer = pdk.Layer(
            'HeatmapLayer',
            data=df_filtered,
            get_position='[lon, lat]',
            get_weight=weight_column,
            opacity=0.8,
            threshold=0.3, # ใช้ในการกำหนดความเข้มข้น
            radius_pixels=30,
        )
        tooltip_data = {"text": "Avg Price: {Avg_Price}"}

    elif layer_type == "problem":
        st.subheader("Community Challenges (Problem Intensity)")
        st.caption("Visualizes the reported frequency and severity of problems using the angry score as intensity weight.")     

        # คำนวณค่าน้ำหนัก: Total_Problems * Norm_Weight
        df['weight_value'] = df['Total_Problems'] * df['Norm_Weight']
        weight_column = 'weight_value'

        # PyDeck Heatmap Layer
        layer = pdk.Layer(
            'HeatmapLayer',
            data=df,
            get_position='[lon, lat]',
            get_weight=weight_column,
            opacity=0.9,
            threshold=0.3,
            radius_pixels=30,
        )
        tooltip_data = {"text": "Intensity: {weight_value:.2f}"}

    elif layer_type == "livability":
        st.subheader("Overall Livability Score")
        st.caption("Presents a composite index score representing the overall quality of life, based on amenities, green space access, and public transport.")
        
        # ใช้ Livability_Score_10 เป็นค่าน้ำหนัก
        df['weight_value'] = df['Livability_Score_10']
        weight_column = 'weight_value'

        # PyDeck Heatmap Layer
        # กำหนดสีเป็น 'gradient' เพื่อให้ Livability Score สูงเป็นสีเขียว
        # NOTE: PyDeck Heatmap ใช้สี Gradient ได้ แต่การตั้งค่าจะซับซ้อนกว่า Folium
        # ในที่นี้ใช้ค่า default เพื่อให้เห็นความแตกต่างของน้ำหนัก
        layer = pdk.Layer(
            'HeatmapLayer',
            data=df,
            get_position='[lon, lat]',
            get_weight=weight_column,
            opacity=0.8,
            threshold=0.5,
            radius_pixels=30,
        )
        tooltip_data = {"text": "Livability Score: {Livability_Score_10}"}

    else:
        st.error("Invalid layer_type!")
        return

    # 3. สร้างและแสดงผล PyDeck Chart
    if layer:
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style=pdk.map_styles.DARK,
                tooltip=tooltip_data # แสดงข้อมูลเมื่อนำเมาส์ไปชี้
            ),
            use_container_width=True # ทำให้แผนที่เต็มความกว้าง
        )

     
#--bubble
def create_bubble_chart(df: pd.DataFrame):
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    selected_year = st.slider(
        "Select Year",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        help="Move the slider to explore different years!"
    )

    df_year = df[df['year'] == selected_year].copy()
    df_year["problem_intensity"] = df_year["problem_count_500m"] * df_year["angry_score"]

    df_group = df_year.groupby("district").agg(
        avg_livability=("livability_score", "mean"),
        avg_problem_intensity=("problem_intensity", "mean"),
        avg_price_sqm=("Avg_Price", "mean"),
        project_count=("project_name", "count")
    ).reset_index()

    fig = px.scatter(
        df_group,
        x="avg_livability",
        y="avg_problem_intensity",
        size="avg_price_sqm",
        color="district",
        hover_name="district",
        size_max=35,
        opacity=0.85,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        marker=dict(
            line=dict(width=2, color="white")
        )
    )

    fig.update_traces(
        selector=dict(mode="markers"),
        selected=dict(marker=dict(size=55, opacity=1)),  # เด่นมาก
        unselected=dict(marker=dict(size=0.01, opacity=0))  # ซ่อนทั้งหมด
    )

    fig.update_layout(
        clickmode="event+select",
        legend=dict(
            itemclick="toggleothers",     # คลิก legend = โชว์เฉพาะเขตนั้น
            itemdoubleclick="toggleothers"  # ดับเบิลคลิก = โชว์เฉพาะเขตนั้นเหมือนกัน
        ),
        title=dict(text=f"Bubble Chart by District — {selected_year}", x=0.35),
        plot_bgcolor="#F9FAFF",
        paper_bgcolor="#F5F6FF",
        width=1000,
        height=620
    )

    st.plotly_chart(fig, use_container_width=True)

def map_value_to_color(value, vmin, vmax, color_range):
    """ฟังก์ชันช่วยสำหรับแปลงค่าตัวเลขเป็นสีตามช่วง (Gradient)"""
    if pd.isna(value): return [0, 0, 0, 0] # Handle NaN
    if vmax == vmin: return color_range[-1] 
    
    # Normalize 0-1
    norm = (value - vmin) / (vmax - vmin)
    idx = int(norm * (len(color_range) - 1))
    return color_range[idx]

def create_district_column_map(df, center_lat=13.7563, center_lon=100.5018, color_preset="red"):
    """
    สร้างแผนที่ 3D Column Chart แบ่งตามเขต
    df: DataFrame ที่มี columns ['lat', 'lon', 'Total_Problems', 'district']
    """
    # 1. กำหนด Palette
    if color_preset == "red": 
        # โทน เหลือง -> ส้ม -> แดง (สำหรับปัญหา)
        color_range = [
            [255, 237, 160, 200], 
            [254, 217, 118, 200], 
            [253, 141, 60, 200],  
            [227, 26, 28, 200],   
            [189, 0, 38, 200]     
        ]
        target_col = "Total_Problems"
        elevation_scale = 10
        
    else: # Default หรือ Green (สำหรับ Livability/Price)
        color_range = [
            [237, 248, 251, 200], [178, 226, 226, 200],
            [102, 194, 164, 200], [44, 162, 95, 200], [0, 109, 44, 200]
        ]
        target_col = "Livability_Score_10" # สมมติใช้ column นี้ถ้าเป็นสีเขียว
        elevation_scale = 10

    # 2. เตรียมข้อมูลสี (Color Mapping)
    df = df.copy()
    vmin = df[target_col].min()
    vmax = df[target_col].max()
    
    # สร้าง column สีสำหรับแต่ละแถว
    df['fill_color'] = df[target_col].apply(lambda x: map_value_to_color(x, vmin, vmax, color_range))

    # 3. สร้าง Layer
    layer = pdk.Layer(
        "ColumnLayer",
        df,
        get_position=['lon', 'lat'],
        get_elevation=target_col,     # ความสูงตามค่าข้อมูล
        get_fill_color="fill_color",  # สีตามที่คำนวณไว้
        elevation_scale=elevation_scale,
        radius=800,                   # รัศมีแท่งกราฟ (เมตร)
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # 4. View State
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=60,
        bearing=0
    )

    # 5. Tooltip
    tooltip = {
        "html": f"<b>District:</b> {{district}}<br/><b>Value:</b> {{{target_col}}}",
        "style": {"color": "white", "backgroundColor": "#333"}
    }

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )

# --- Prediction Line Chart ---
def create_prediction_chart(current_price, selected_problems):
    """
    สร้างกราฟเส้นทำนายราคา 5 ปีข้างหน้า เปรียบเทียบระหว่าง
        1. Base Case (โตตามเงินเฟ้อปกติ)
        2. Improved Case (โตขึ้นหากแก้ปัญหาเมืองที่เลือก)
    """
    years = list(range(2025, 2031))
    
    # สมมติฐาน: ราคาคอนโดโตปีละ 3%
    base_growth_rate = 0.03 
    
    # สมมติฐาน: ปัญหาแต่ละอย่างถ้าแก้ได้ จะช่วยดันราคาขึ้นอีกอย่างละ 1.5%
    uplift_per_problem = 0.015 
    extra_growth = len(selected_problems) * uplift_per_problem

    data = []
    
    price_base = current_price
    price_improved = current_price

    for year in years:
        # Base Scenario
        price_base = price_base * (1 + base_growth_rate)
        # Improved Scenario
        price_improved = price_improved * (1 + base_growth_rate + extra_growth)
        
        data.append({"Year": str(year), "Price": round(price_base), "Scenario": "Base Case"})
        data.append({"Year": str(year), "Price": round(price_improved), "Scenario": "Improved Case (Solved)"})

    df_predict = pd.DataFrame(data)

    chart = alt.Chart(df_predict).mark_line(point=True).encode(
        x=alt.X('Year', title='Year'),
        y=alt.Y('Price', title='Predicted Price (THB/sqm)', scale=alt.Scale(zero=False)),
        color=alt.Color('Scenario', legend=alt.Legend(title="Scenario", orient="bottom")),
        tooltip=['Year', 'Price', 'Scenario']
    ).properties(
        # title=f"5-Year Price Prediction (Impact: +{extra_growth*100:.1f}% Growth Rate)",
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

# --- Problem Distribution Chart ---
def create_problem_distribution_chart(df_summary_problem):
    if df_summary_problem.empty:
        st.warning("No problem data available.")
        return
    
    # Data Preparation
    type_sums = df_summary_problem.copy()

    if 'Problem_Type' in type_sums.columns and 'Total_Count' in type_sums.columns:
        type_sums = type_sums.rename(columns={'Problem_Type': 'problem_type', 'Total_Count': 'count'})
    else:
        type_sums.columns = ['problem_type', 'count']

    type_sums['problem_type'] = type_sums['problem_type'].astype(str).str.replace('type_', '')
    type_sums['count'] = pd.to_numeric(type_sums['count'], errors='coerce').fillna(0)
    
    # 1. Base Chart (main X, Y)
    max_val = type_sums['count'].max()
    tick_values = list(range(0, int(max_val) + 5000, 5000))
    base = alt.Chart(type_sums).encode(
        y=alt.Y('problem_type', sort='-x', title='Category'),
        x=alt.X('count', title='Number of Reports', scale=alt.Scale(domainMin=0), axis=alt.Axis(values=tick_values)),
        tooltip=[
            alt.Tooltip('problem_type', title='Category'),
            alt.Tooltip('count', title='Count', format=',d')
        ]
    )

    # 2. Layer Bar
    bars = base.mark_bar().encode(
        color=alt.Color('count', legend=None, scale=alt.Scale(scheme='blues'))
    )

    # 3. Layer Text Label
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text=alt.Text('count', format=',d')
    )

    # 4. Bars + Text
    chart = (bars + text).properties(
        title="Distribution of Reported Problems (Traffy Fondue)",
        height=max(400, len(type_sums) * 45)
    ).interactive(bind_x=False)

    st.altair_chart(chart, use_container_width=True)