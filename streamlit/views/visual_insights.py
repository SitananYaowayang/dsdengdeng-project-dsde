import streamlit as st
import pandas as pd
import pydeck as pdk
from viz_components import create_single_layer_heatmap, create_bubble_chart, create_district_column_map, create_price_column_map # create_grid_map,

def show(df_condos, df_problems, df_district_summary):
    # --- 1. Heatmap ---
    st.header("Heatmap")

    Heatmap_Layer = ["Condominium Pricing (Price per Square Meter)", 
            "Community Challenges (Problem Intensity)", 
            "Overall Livability (Livability Score)"]
    layer_option=st.selectbox("Select Heatmap Layer",Heatmap_Layer)

    layer_map = {
        "Condominium Pricing (Price per Square Meter)": "price",
        "Community Challenges (Problem Intensity)": "problem",
        "Overall Livability (Livability Score)": "livability"
    }
    selected_layer = layer_map[layer_option]
    if not df_district_summary.empty:
        create_single_layer_heatmap(df_district_summary, layer_type=selected_layer)
    else:
        st.warning("Cannot display map: No data or lat/lon missing.")

    # --- 2. Grid Map Analysis ---
    st.header("Grid Map Analysis (3D Density)")
    
    tab1, tab2 = st.tabs(["Problem Density", "Price Analysis"])
    
    # Tab 1: City Problems
    with tab1:
        st.subheader("Community Challenges (By District)")

        if not df_district_summary.empty:
            map_problems = create_district_column_map(
                df_district_summary,
                color_preset="red"
            )
            st.pydeck_chart(map_problems)
            
            # (Option) แสดงตารางข้อมูลประกอบ
            with st.expander("ดูข้อมูลรายเขต"):
                st.dataframe(df_district_summary.sort_values('Total_Problems', ascending=False))

            st.caption("Data Source: Real Traffy Fondue Data (Aggregated by District)")
        else:
            st.info("ไม่พบข้อมูลปัญหา (df_problems is empty)")

    # Tab 2: 3D Condo Price Density
    with tab2:
        st.subheader("Condominium Pricing (Price per Sq.M.)")

        if not df_district_summary.empty:
            map_price_3d = create_price_column_map(df_district_summary)
            st.pydeck_chart(map_price_3d)

            with st.expander("ดูข้อมูลคอนโด"):
                st.dataframe(df_district_summary[['district', 'Avg_Price_Per_SqM']].sort_values('Avg_Price_Per_SqM', ascending=False))

            st.caption("Data Source: DDProperty Data")
        else:
            st.info("ไม่พบข้อมูลคอนโด (df_condos is empty)")


    st.markdown("---")

    # --- 3. Bubble Chart ---
    st.header("Interactive Bubble Chart")
    if not df_district_summary.empty: 
        create_bubble_chart(df_district_summary)
    else:
        # อัปเดตข้อความเตือนให้สั้นลง
        st.warning("🚨 Bubble Chart data is empty or missing.")
    st.markdown("---")