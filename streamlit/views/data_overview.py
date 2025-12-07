# Page 3
import pandas as pd
import streamlit as st
from viz_components import create_problem_distribution_chart

def show(df_condos, df_summary_problem):
    st.header("Data Overview & Sources")

    if df_condos is None:
        df_condos = pd.DataFrame()
    if df_summary_problem is None:
        df_summary_problem = pd.DataFrame()

    # --- 1. Top Level Metrics ---
    st.subheader("Top Level Metrics")
    col_ov_1, col_ov_2, col_ov_3 = st.columns(3)
    
    with col_ov_1:
        # Update: Calculate total sum from the summary table
        if not df_summary_problem.empty and 'Total_Count' in df_summary_problem.columns:
            total_problems = df_summary_problem['Total_Count'].sum()
        else:
            total_problems = 0
            
        st.metric("Total Reported Issues", f"{total_problems:,}")
        st.markdown("""Source: [TraffyFondue](https://bangkok.traffy.in.th/)""")
    
    with col_ov_2:
        total_projects = len(df_condos)
        st.metric("Total Condo Projects", f"{total_projects:,}")
        st.markdown("""Source: [LivingInsider](https://www.livinginsider.com/)""")
        
    with col_ov_3:
        avg_price_all = df_condos['price_sqm'].mean() if not df_condos.empty else 0
        st.metric("City-wide Avg Price", f"฿{avg_price_all:,.0f}")

    st.markdown("---")

    # --- 2. Problem Distribution Chart ---
    st.subheader("Reported Issue Distribution")

    if not df_summary_problem.empty:
        create_problem_distribution_chart(df_summary_problem)
    else:
        st.info("No problem data loaded.")

    st.markdown("---")