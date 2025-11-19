import google.generativeai as genai
import json


# 1. Setup Gemini (แนะนำใช้ Flash เพราะฟรี/ถูก และเร็วสำหรับงาน Text เยอะๆ)
genai.configure(api_key="AIzaSyA3bKAzzE6hlYcDBK6vSqR6IDdE3KCWzg4")
model = genai.GenerativeModel('gemini-2.5-flash',
                              generation_config={"response_mime_type": "application/json"})

# สมมติข้อมูล (ดึงมาจาก DataFrame ของคุณ)
# แปลง Dataframe เป็น List of Dicts เพื่อส่งเข้า Batch
data_batch = [
    {"id": "101", "comment": "ป้ายจราจรบอกทางไปสถานที่สวพ.91(กรุงเทพ) หลุดจากการที่เจ้าหน้าที่ก่อสร้างถอดออกและไม่ติดตั้งไว้แบบเดิม  โปรดส่งเจ้าหน้าที่มาซ่อมแซมเพื่อประโยชน                          น์ในการบอกทางให้กับประชาชนผู้มาติดต่อราชการ ขณะนี้ป้ายถูกเก็บไว้ที่สถานที่สวพ.91 (กรุงเทพ) โปรดติดต่อรับป้ายที่เจ้าหน้าที่ สวพ.91(กรุงเทพ)โทร. 02-562-003                            35 \n062-192-3532 \n\nหมายเหตุ  ขณะนี้ป้ายไม่ได้อยู่ข้างตู้ไปรษณีย์ริมถนน แต่ถูกเก็บรักษาไว้ที่หน่วยงาน สวพ.91(กรุงเทพ) หาก\nกทม.จะทำการแก้ไขและติดตั้งป้                           ายให้เป็นปกติ โปรดติดต่อแจ้งรับป้ายก่อนจะได้ไม่เสียเวลาไปและไม่เจอป้าย"},
    {"id": "102", "comment": "อเสาไฟริมคลองไม่ได้เปิดมาหลายวัน"},
    {"id": "103", "comment": "🔊 แจ้งพบคนมานอนบนสะพนาบอยคนข้าม น่าจะคนไร้บ้าน จึงรบกวนเจ้าหน้าที่ตรวจสอบ เพราะไม่แน่ใจอาการอื่น\n📌ตรงสะ             ะพานลอยคนข้ามแยก โพธิ์แก้ว\n🙏👷👷‍♀️👷‍♂️ขอของคุณ ในการจัดการปัญหานี้🥀✌️✌️👏👏👏"},
    {"id": "104", "comment": "ไฟกิ่งดับมืดตึ๊ดตื๋อเลย เปลี่ยวมาก กลัวโดนปล้น"}
]

# 2. Create Prompt
prompt = f"""
You are an Urban Analyst. Analyze these complaints using Chain-of-Thought reasoning.
Determine the 'Severity' (1-5) based on risk to safety and urgency.

=== Scoring Rules (Rubric) ===
1 = General / Inquiry (non-hazardous issues such as advertisements, tall grass, general information requests)
2 = Minor nuisance (slightly overgrown grass, mildly uneven pavement, dirty stains)
3 = Disturbance (affects daily life, e.g., foul odors, broken sidewalks, overflowing trash, minor flooding after rain, emerging pests or animals)
4 = Safety hazard (deep potholes, damaged manhole covers, falling tree branches, low-hanging electrical wires)
5 = Dangerous / Urgent (risk of injury or death, e.g., missing manhole covers, fire, structurally damaged buildings at risk of collapse, severe flooding entering homes)

=== Example Analyses ===
User Input: "I want to know what day the welfare allowance will be deposited."
AI Output: {{ "id": "sample_1", "reasoning": "This is only a request for information, not a complaint about any damage or hazard.", "severity": 1 }}

User Input: "A campaign sign is blocking the sidewalk and covering the street sign. It looks messy. Please remove it."
AI Output: {{ "id": "sample_2", "reasoning": "This is an issue about aesthetics and public order, but not severe enough to obstruct movement completely.", "severity": 1 }}

User Input: "The water smells rotten and there are many mosquitoes. I'm afraid of dengue fever."
AI Output: {{ "id": "sample_3", "reasoning": "This affects hygiene and health, causing disturbance to daily living.", "severity": 2 }}

User Input: "Trash has been dumped on the sidewalk at the location above, and there are many rats running around every evening around 7 PM. Many office workers and tourists pass by there. The area is extremely dirty."
AI Output: {{ "id": "sample_4", "reasoning": "This impacts hygiene and health and significantly disturbs daily life.", "severity": 3 }}

User Input: "There is a pothole about 10 cm deep in the left lane. Two motorcycles have already fallen because of it today."
AI Output: {{ "id": "sample_5", "reasoning": "There is a high risk of serious accidents. This is a dangerous situation.", "severity": 4 }}

User Input: "The manhole cover in front of the school is missing. A child could fall right into it. Very dangerous!"
AI Output: {{ "id": "sample_6", "reasoning": "This poses a high risk of serious injuries, especially to children. Extremely dangerous.", "severity": 5 }}

=== Your Task ===
Analyze the following input according to the format above.
Use English when explaining the reasoning.

Input Data:
{json.dumps(data_batch, ensure_ascii=False)}

Output Requirement:
Provide a JSON list. Keys: 'id', 'category', 'reasoning' (brief CoT), 'severity' (int).
"""

# 3. Call API (Simulate the loop)
try:
    response = model.generate_content(prompt)
    raw_text = response.text
    
    # === ส่วนที่เพิ่มมา: Clean Data ก่อนแปลง ===
    # ลบ Markdown Code Block (```json และ ```) ออก
    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    # แปลงผลลัพธ์กลับเป็น Python Object
    results = json.loads(clean_text)
    
    print("✅ Success! Here is the data:")
    # แสดงผล
    for res in results:
        print(f"ID: {res.get('id')} | Severity: {res.get('severity')} | Reason: {res.get('reasoning')}")

except json.JSONDecodeError as e:
    print("❌ JSON Error: AI ส่ง format ผิดมาครับ")
    print(f"Error detail: {e}")
    print("--- Raw Output from AI (ไว้ดูว่าผิดตรงไหน) ---")
    print(response.text) # ปริ้นท์ออกมาดูเลยว่ามันส่งอะไรมา
except Exception as e:
    print(f"❌ Error: {e}")