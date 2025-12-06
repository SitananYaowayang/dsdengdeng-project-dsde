# Page 3
import streamlit as st
from viz_components import create_problem_distribution_chart

def show(df_condos, df_problems):
    st.header("Data Overview & Sources")

    # --- 1. Top Level Metrics ---
    st.subheader("Top Level Metrics")
    col_ov_1, col_ov_2, col_ov_3 = st.columns(3)
    
    with col_ov_1:
        total_problems = len(df_problems) if not df_problems.empty else 0
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

    if not df_problems.empty:
        create_problem_distribution_chart(df_problems)
    else:
        st.info("No problem data loaded.")

    st.markdown("---")

    # --- 3. Sample Raw Data ---
    st.subheader("Sample Raw Data")
    tab1, tab2 = st.tabs(["Condos", "Problems"])
        
    with tab1:
        st.dataframe(df_condos[['project_name', 'district', 'price_sqm']].head(10), use_container_width=True)
        
    with tab2:
        if not df_problems.empty:
            st.dataframe(df_problems[['ticket_id', 'type', 'district', 'status']].head(10), use_container_width=True)
        else:
            st.write("No data.")

    st.markdown("---")