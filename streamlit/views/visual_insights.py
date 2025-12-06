import streamlit as st
from viz_components import create_single_layer_heatmap, create_bubble_chart



def show(df_condos, center_lat, center_lon):
    # --- 1. Heatmap ---
    st.header("Heatmap")

    Heatmap_Layer = ["Condominium Pricing (Price per Square Meter)", 
            "Community Challenges (Problem Intensity)", 
            "Overall Livability (Livability Score)"]
    layer_option=st.selectbox("Select Heatmap Layer",Heatmap_Layer)
    
    #st.slider("ช่วงราคา (ต่อ ตร.ม.):", 50000, 300000)

    layer_map = {
        "Condominium Pricing (Price per Square Meter)": "price",
        "Community Challenges (Problem Intensity)": "problem",
        "Overall Livability (Livability Score)": "livability"
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