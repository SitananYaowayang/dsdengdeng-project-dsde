# viz_functions.py
import streamlit as st
import pandas as pd
import altair as alt
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

    # Count problems for each type
    df_count = df_problems['type'].value_counts().reset_index()
    df_count.columns = ['Problem Type', 'Count']

    chart = alt.Chart(df_count).mark_bar().encode(
        x=alt.X('Problem Type', sort='-y', title='Category'),
        y=alt.Y('Count', title='Number of Reports'),
        color=alt.Color('Problem Type', legend=None),
        tooltip=['Problem Type', 'Count']
    ).properties(
        title="Distribution of Reported Issues (Traffy Fondue)",
        height=350
    ).interactive()

    st.altair_chart(chart, use_container_width=True)