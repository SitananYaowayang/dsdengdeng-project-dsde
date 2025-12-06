# Page 2
import streamlit as st
from viz_components import create_prediction_chart

def show(df_condos):
    st.header("Future Price Prediction")
    st.caption("จำลองสถานการณ์ราคาคอนโดในอีก 5 ปีข้างหน้า หากปัญหาเมืองในพื้นที่ได้รับการแก้ไข")

    # --- 1. Select District ---
    district_list = sorted(df_condos['district'].unique().tolist()) if not df_condos.empty else []
    selected_district_pred = st.selectbox("🔍Select District:", district_list, index=0 if district_list else None)

    # กรองข้อมูลเฉพาะเขตที่เลือก
    df_district = df_condos[df_condos['district'] == selected_district_pred]
    
    # คำนวณค่าปัจจุบัน
    if not df_district.empty:
        current_price = df_district['price_sqm'].mean()
        current_liva = df_district['livability_score'].mean()
    else:
        current_price = 0
        current_liva = 0

    # --- 2. Current Stats & Simulator Controls ---
    col_sim_1, col_sim_2 = st.columns([1, 3])

    with col_sim_1:
        st.subheader(f"📍 {selected_district_pred}")
        st.metric("ราคาเฉลี่ยปัจจุบัน (บาท/ตร.ม.)", f"฿{current_price:,.0f}")
        st.metric("คะแนนความน่าอยู่ (Livability)", f"{current_liva:.2f} / 10")
                
    with col_sim_2:
        st.subheader("เลือกปัญหาที่คาดว่าจะได้รับการแก้ไข")
        st.caption("การเลือกแก้ไขปัญหาจะช่วยเพิ่ม Growth Rate ของราคา")
        
        problem_options = ['ถนน', 'ทางเท้า', 'ความปลอดภัย', 'แสงสว่าง', 'ความสะอาด', 'กีดขวาง', 'ท่อระบายน้ำ', 'น้ำท่วม', 'ต้นไม้', 'PM2.5', 'จราจร', 'สะพาน']
        selected_fixes = []

        sub_cols = st.columns(3)
        for i, p in enumerate(problem_options):
            col_idx = i // 4 
            if col_idx < len(sub_cols):
                with sub_cols[col_idx]:
                    # เพิ่ม key เพื่อป้องกัน DuplicateWidgetID
                    if st.checkbox(f"{p}", value=False, key=f"chk_{p}"):
                        selected_fixes.append(p)

    # --- 3. Prediction Chart ---
    st.subheader("5-Year Price Prediction")
    st.caption("กราฟเส้นทำนายราคา 5 ปีข้างหน้า เปรียบเทียบระหว่าง Base Case (โตตามเงินเฟ้อปกติ) และ Improved Case (โตขึ้นหากแก้ปัญหาเมืองที่เลือก)")
    if current_price > 0:
        create_prediction_chart(current_price, selected_fixes)
    else:
        st.error("ไม่พบข้อมูลราคาในเขตนี้")

    st.markdown("---")