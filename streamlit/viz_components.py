# viz_functions.py
import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
from folium.plugins import HeatMap, MiniMap,MeasureControl
from branca.element import Template, MacroElement
import math

# ---heatmap
def create_single_layer_heatmap(df, center_lat, center_lon, layer_type="price", map_key="single_map"):
    """
    layer_type: 'price', 'problem', 'livability'
    """
    if layer_type == "price":
        st.subheader("Condominium Pricing (Price per Sq.M.)")
        st.caption("Displays the average selling price per square meter and highlights price trends for condo units.")

        scale = 10 ** (len(str(df['price_sqm'].min())) - 2)
        rounded_min = df['price_sqm'].min() - (df['price_sqm'].min() % scale)
        scale_max = 10 ** (len(str(int(df['price_sqm'].max()))) - 2)
        rounded_max = ((df['price_sqm'].max() + scale_max - 1) // scale_max) * scale_max

        selected_price_range = st.slider(
            "ช่วงราคา (ต่อ ตร.ม.):",
            min_value=rounded_min,
            max_value=rounded_max,
            value=(
                int(df['price_sqm'].quantile(0.2)),   
                int(df['price_sqm'].quantile(0.7))    
            ),
            step=1000,
        )
        df_filtered = df[
            (df['price_sqm'] >= selected_price_range[0]) &
            (df['price_sqm'] <= selected_price_range[1])
        ].copy()
        if df_filtered.empty:
            st.warning("No condos found within the selected price range 🙅‍♀️")
            return
        
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
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="cartodbpositron")
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
        avg_price_sqm=("price_sqm", "mean"),
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

# --- 2. Grid Map (PyDeck) ---
# def create_grid_map(df, center_lat, center_lon, cell_size=300, target_col=None, aggregation="SUM", color_preset="red"):
#     needed_cols = ['lat', 'lon']
#     if target_col:
#         needed_cols.append(target_col)
#     mini_df = df[needed_cols]
    
#     if color_preset == "red": # โทนส้ม-แดง (สำหรับปัญหา/ความหนาแน่น)
#         color_range = [
#             [255, 255, 178, 200], [254, 204, 92, 200], 
#             [253, 141, 60, 200], [240, 59, 32, 200], [189, 0, 38, 200]
#         ]
#         elevation_scale = 50
#     elif color_preset == "green": # โทนเขียว-ฟ้า (สำหรับราคา/มูลค่า)
#         color_range = [
#             [237, 248, 251, 200], [178, 226, 226, 200],
#             [102, 194, 164, 200], [44, 162, 95, 200], [0, 109, 44, 200]
#         ]
#         elevation_scale = 10
#     else: # Default
#         color_range = [[255, 140, 0, 200]]
#         elevation_scale = 10

#     layer = pdk.Layer(
#         "GridLayer",
#         mini_df,
#         pickable=True,
#         extruded=True,
#         cell_size=cell_size,
#         elevation_scale=elevation_scale,
#         get_position=['lon', 'lat'], 
#         color_range=color_range,
#         get_elevation_weight=target_col,
#         aggregation=aggregation,
#     )

#     view_state = pdk.ViewState(
#         latitude=center_lat,
#         longitude=center_lon,
#         zoom=11,
#         pitch=45,
#         bearing=0
#     )

#     tooltip_html = "<b>Value:</b> {elevationValue}<br/>Lat: {position.1}<br/>Lon: {position.0}"
#     if target_col:
#         tooltip_html = f"<b>{target_col}:</b> {{elevationValue}}<br/>Lat: {{position.1}}<br/>Lon: {{position.0}}"

#     return pdk.Deck(
#         layers=[layer],
#         initial_view_state=view_state,
#         tooltip={"html": tooltip_html, "style": {"color": "white"}}
#     )

def create_district_column_map(df, center_lat, center_lon, color_preset="red"):
    if color_preset == "red":
        fill_color = [200, 30, 30, 200]
    elif color_preset == "green":
        fill_color = [0, 150, 0, 200]
    else:
        fill_color = [255, 140, 0, 200]

    layer = pdk.Layer(
        "ColumnLayer",
        df,
        get_position=['lon', 'lat'], # ใช้ lat/lon ของจุดกึ่งกลางเขต
        get_elevation="count",       # ความสูงตามจำนวนเรื่อง
        elevation_scale=5,
        radius=800,
        get_fill_color=fill_color,
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=10,
        pitch=60,
        bearing=0
    )

    tooltip = {
        "html": "<b>District:</b> {district}<br/><b>Total Problems:</b> {count}",
        "style": {"color": "white"}
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
def create_problem_distribution_chart(df_problems):
    if df_problems.empty:
        st.warning("No problem data available.")
        return
    
    # Data Preparation
    type_cols = [col for col in df_problems.columns if col.startswith('type_')]
    if not type_cols:
        st.error("ไม่พบคอลัมน์ type_... ในข้อมูล (ตรวจสอบ Data Loader)")
        return
    
    # Count problems for each type
    type_sums = df_problems[type_cols].sum().reset_index()
    type_sums.columns = ['problem_type', 'count']
    type_sums['problem_type'] = type_sums['problem_type'].str.replace('type_', '')

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
        title="Distribution of Reported Issues (Traffy Fondue)",
        height=max(400, len(type_sums) * 45)
    ).interactive(bind_x=False)

    st.altair_chart(chart, use_container_width=True)