# Page 3
import pandas as pd
import streamlit as st
from viz_components import create_problem_distribution_chart

def show(df_condos, df_problem_summary, df_district_summary):
    st.header("Data Overview & Sources")

    if df_condos is None:
        df_condos = pd.DataFrame()
    if df_problem_summary is None:
        df_problem_summary = pd.DataFrame()
    if df_district_summary is None:
        df_district_summary = pd.DataFrame()

    # --- 1. Top Level Metrics ---
    st.subheader("Top Level Metrics")
    col_ov_1, col_ov_2, col_ov_3 = st.columns(3)
    
    with col_ov_1:
        # 1. Calculate the Unique count (100k) from district summary
        if not df_district_summary.empty and 'Total_Problems' in df_district_summary.columns:
            total_unique_problems = df_district_summary['Total_Problems'].sum()
        else:
            total_unique_problems = 0

        # 2. Calculate the Categorized count (150k) from problem summary
        if not df_problem_summary.empty and 'Total_Count' in df_problem_summary.columns:
            total_categorized_problems = df_problem_summary['Total_Count'].sum()
        else:
            total_categorized_problems = 0

        # Display Unique count as the main metric
        st.metric("Total Reported Problems", f"{total_unique_problems:,}")
        
        # Display the Categorized count as an explanation
        st.markdown(f"""
            <div style="margin-top: -15px; font-size: 14px; color: #666; line-height: 1.4;">
                <em>{total_categorized_problems:,} total problems after categorization (multi-tag).</em>
                <br>
                <div style="margin-top: 6px;">
                    Source: <a href="https://bangkok.traffy.in.th/">TraffyFondue</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_ov_2:
        total_projects = len(df_condos)
        st.metric("Total Condo Projects", f"{total_projects:,}")
        # st.markdown("""Source: [LivingInsider](https://www.livinginsider.com/)""")
        st.markdown(f"""
            <div style="margin-top: -15px; font-size: 14px; color: #666; line-height: 1.4;">
                <span style="visibility: hidden;"><em>{total_categorized_problems:,} total problems...</em></span>
                <br>
                <div style="margin-top: 6px;">
                    Source: <a href="https://www.ddproperty.com/">DDProperty</a> 
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col_ov_3:
        avg_price_all = df_condos['price_per_sqm'].mean() if not df_condos.empty else 0
        st.metric("City-wide Avg Price", f"฿{avg_price_all:,.0f}")

    st.markdown("---")

    # --- 2. Problem Distribution Chart ---
    st.subheader("Reported Problem Distribution")

    if not df_problem_summary.empty:
        create_problem_distribution_chart(df_problem_summary)
    else:
        st.info("No problem data loaded.")

    st.markdown("---")