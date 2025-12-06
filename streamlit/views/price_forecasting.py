import streamlit as st
from datetime import date

def show(df_condos, df_district_summary):
    st.header("Price Forecasting Calculator")
    st.markdown("Estimate condominium prices based on location and unit type (Based on current data)")

    if df_condos.empty:
        st.error("No Data Available")
        return

    # --- 1. Input Section ---
    with st.container():
        st.subheader("🏡 Property Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Select District
            districts = sorted(df_condos['district'].unique().tolist())
            selected_district = st.selectbox("Select District", districts)
            
        with col2:
            # Bedrooms
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=5, value=1, step=1)
            # Bathrooms
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=5, value=1, step=1)

        with col3:
            # Auto-calculate area (Heuristic)
            estimated_area = (bedrooms * 25) + (bathrooms * 10) + 5
            if bedrooms == 0: estimated_area = 25
            
            # Area Size
            area_sqm = st.number_input("Room Size (sq.m.)", min_value=20.0, max_value=500.0, value=float(estimated_area))

            # Target Date
            publish_date = st.date_input("Target Date", value=date.today(), max_value=date.today())

    st.markdown("---")

    # --- 2. Calculation Logic ---
    df_district = df_condos[df_condos['district'] == selected_district]
    
    if df_district.empty:
        st.warning(f"No sales data available for {selected_district}")
        return

    # 2.1 Base Price Calculation (Current Data)
    median_price_sqm = df_district['price_sqm'].median()
    min_price_sqm = df_district['price_sqm'].quantile(0.1)
    max_price_sqm = df_district['price_sqm'].quantile(0.9)

    base_price = median_price_sqm * area_sqm

    # 2.2 Time Adjustment Calculation
    # Assumption: Database prices are "Current"
    days_diff = (publish_date - date.today()).days
    years_diff = days_diff / 365.0
    
    # Compound Interest Formula: Future Price = Present Price * (1 + rate)^years
    # Note: 'time_factor' is currently set to 1 (No growth rate applied in this snippet)
    time_factor = 1 
    
    final_predicted_price = base_price * time_factor
    final_min_price = (min_price_sqm * area_sqm) * time_factor
    final_max_price = (max_price_sqm * area_sqm) * time_factor
    
    price_change = final_predicted_price - base_price

    # --- 3. Display Result ---
    st.subheader(f"Estimation Result: {selected_district}")

    # Display Metrics
    m1, m2 = st.columns([2, 1])
    
    with m1:
        st.metric(
            label=f"Estimated Price on {publish_date.strftime('%d/%m/%Y')}",
            value=f"{final_predicted_price:,.0f} THB",
            delta=f"{price_change:,.0f} THB (Time Adjustment)" if abs(price_change) > 100 else None
        )
        st.info(f"Market Range: **{final_min_price:,.0f} - {final_max_price:,.0f} THB**")

    with m2:
        st.caption(f"Time Horizon: {years_diff:.2f} Years")
        st.caption(f"District Base Price: {median_price_sqm:,.0f} THB/sq.m.")
        # st.caption(f"District Base Price: {median_price_sqm:,.0f} THB/sq.m.")

    # --- 4. Supporting Data ---
    with st.expander("View Reference Data in this District"):
        st.write(f"Current market prices in **{selected_district}** (Time unadjusted)")
        st.dataframe(
            df_condos[['project_name', 'price_sqm']]
            .sort_values('price_sqm', ascending=False)
            .style.format({'price_sqm': '{:,.0f}'})
        )