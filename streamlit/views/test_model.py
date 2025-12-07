import streamlit as st
from model.prediction_service import CondoPricePredictor

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Condo Price Predictor", page_icon="🏢")

# 2. โหลดโมเดล (ใช้ @st.cache_resource เพื่อโหลดแค่ครั้งเดียว ไม่โหลดใหม่ทุกครั้งที่กดปุ่ม)
@st.cache_resource
def load_model():
    return CondoPricePredictor()

try:
    ai = load_model()
    # ดึงรายชื่อเขตทั้งหมดมาทำ Dropdown
    district_list = list(ai.score_map.keys())
    district_list.sort() # เรียงตามตัวอักษร
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดโมเดล: {e}")
    st.stop()

# 3. ส่วนหัวของเว็บ
st.title("🏢 ทำนายราคาคอนโด กทม.")
st.write("ระบบประเมินราคาคอนโดด้วย AI ผสานข้อมูล **Livability Score**")

st.markdown("---") # เส้นขีดคั่น

# 4. สร้าง Form รับข้อมูล (ด้านซ้าย-ขวา)
col1, col2 = st.columns(2)

with col1:
    usable_area = st.number_input("พื้นที่ใช้สอย (ตร.ม.)", min_value=10.0, value=35.0, step=1.0)
    bedroom = st.number_input("จำนวนห้องนอน", min_value=0.0, value=1.0, step=1.0)

with col2:
    restroom = st.number_input("จำนวนห้องน้ำ", min_value=1.0, value=1.0, step=1.0)
    # ใช้ Selectbox ให้เลือกเขต แทนการพิมพ์เอง (ป้องกัน Typo)
    district_name = st.selectbox("เลือกเขต", district_list)

# แสดงคะแนน Livability ของเขตที่เลือกทันที
score = ai.get_livability_score(district_name)
st.info(f"📍 เขต **{district_name}** มีคะแนนความน่าอยู่ (Livability Score): **{score:.2f}/10**")

# 5. ปุ่มกดทำนาย
if st.button("💰 ประเมินราคา", type="primary", use_container_width=True):
    with st.spinner('กำลังคำนวณ...'):
        try:
            # เรียกใช้ฟังก์ชัน predict จากคลาสที่คุณเขียนไว้
            price = ai.predict(
                usable_area=usable_area,
                bedroom=bedroom,
                restroom=restroom,
                district_name=district_name
            )
            
            # 6. แสดงผลลัพธ์
            st.success("ประเมินเรียบร้อย!")
            st.metric(label="ราคาประเมิน", value=f"{price:,.0f} บาท")
            
            # (แถม) คำนวณราคาต่อตารางเมตรให้ดูด้วย
            price_per_sqm = price / usable_area
            st.caption(f"เฉลี่ยตารางเมตรละ {price_per_sqm:,.0f} บาท")
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

# Footer
st.markdown("---")
st.caption("Developed by Data Science Team | Model: XGBoost + Traffy Fondue Data")