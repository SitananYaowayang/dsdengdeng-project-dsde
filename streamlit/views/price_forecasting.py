import streamlit as st
from datetime import date
import numpy as np
from data_loader import load_model

def show(df_condos):
    st.header("AI Selling Price Valuation")
    st.markdown("AI-powered Condo **Selling Price** Valuation System (XGBoost) combined with **Livability Score** data")

    # --- 1. Load Model ---
    try:
        AI = load_model()
    except Exception as e:
        st.error(f"An error occurred while loading the model price: {e}")
        st.stop()

    if df_condos.empty:
        st.warning("No Data Available")
        return
    
    st.markdown("---")

    # --- 1. Input Section ---
    with st.container():
        st.subheader("🏡 Property Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            districts = sorted(AI.df_scores.index.tolist()) # Note: index is 'district' now
            selected_district = st.selectbox("Select District", districts)

            try:
                # If using the method directly (recommended if you implement it)
                if hasattr(AI, 'get_district_features'):
                     # We get both scores, we just want the first one (livability)
                     score, _ = AI.get_district_features(selected_district)
                else:
                    # Fallback to dataframe lookup
                    match_row = AI.df_scores.loc[selected_district]
                    score = match_row['Livability_Score'] 
                
                st.info(f"District **{selected_district}** has a Livability Score of: **{score:.2f}/10**")
            except Exception:
                st.caption("Cannot retrieve Livability Score")
            
        with col2:
            # Bedrooms
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=1, step=1)
            # Restrooms
            restrooms = st.number_input("Restrooms", min_value=1, max_value=10, value=1, step=1)

            # Auto-calculate area (Heuristic)
            estimated_area = (bedrooms * 25) + (restrooms * 10) + 5
            if bedrooms == 0: estimated_area = 25
            
            # Area Size
            area_sqm = st.number_input("Room Size (sq.m.)", min_value=16.0, max_value=500.0, value=float(estimated_area))
    st.markdown("---")

    # --- 3. Prediction Logic ---
    if st.button("Evaluate Selling Price", type="primary", use_container_width=True):
        # AI is analyzing data and evaluating the price...
            try:
                log_predicted_price = AI.predict(
                    usable_area=area_sqm,
                    bedroom=bedrooms,
                    restroom=restrooms,
                    district_name=selected_district
                )
                predicted_price = np.exp(log_predicted_price)

                # --- 4. Display Result ---
                st.success("✅ Evaluation Complete")
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(
                        label="Estimated Selling Price",
                        value=f"฿{predicted_price:,.0f}"
                    )
                with res_col2:
                    # Calculate price per square meter for the user's reference
                    price_per_sqm = predicted_price / area_sqm if area_sqm > 0 else 0
                    st.metric(
                        label="Average Price per Sq.m.",
                        value=f"฿{price_per_sqm:,.0f} / Sq.m."
                    )

            except Exception as e:
                # An error occurred during prediction: {e}
                st.error(f"An error occurred during prediction: {e}")
                st.markdown("""
                    **Suggestion:** * Check that the files `xgboost_condo_price_model.pkl` and `imputer_values.pkl` are present in the `model/` folder.
                    * Check that the district name matches what the model recognizes.
                """)

    # --- 5. Supporting Data ---
    # Display project data in this district for comparison (Reference)
    with st.expander(f"🔎 View reference condominiums in {selected_district} district"):
        df_ref = df_condos[df_condos['district_original'] == selected_district]
        if not df_ref.empty:
            st.dataframe(
                df_ref[['district_original', 'title', 'bedroom', 'restroom', 'usable_area', 'price', 'price_per_sqm']]
                .sort_values('price_per_sqm', ascending=False)
                .head(10)
                .style.format({
                'bedroom': '{:.0f}',        # Integer (0 decimal)
                'restroom': '{:.0f}',       # Integer (0 decimal)
                'usable_area': '{:,.1f}',   # Float (1 decimal)
                'price': '{:,.2f}',         # Float (2 decimal)
                'price_per_sqm': '{:,.2f}'  # Float (2 decimal)
            })
            )
        else:
            st.info("No reference project data in the system")