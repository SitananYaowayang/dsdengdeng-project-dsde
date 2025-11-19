import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# ฟังก์ชันสำหรับดึงข้อมูลจาก 1 หน้าประกาศ
def scrape_condo_detail(driver, url):
    print(f"กำลังดึงข้อมูล: {url}")
    driver.get(url)
    
    # Random delay เล็กน้อยเพื่อให้เหมือนคน
    time.sleep(random.uniform(3, 5))
    
    # -------------------------------------------------------
    # 1. กดปุ่ม "ข้อมูลเพิ่มเติม..." (ถ้ามี)
    # -------------------------------------------------------
    try:
        # หาปุ่มที่มี class font_title_more
        read_more_btn = driver.find_element(By.CSS_SELECTOR, ".font_title_more")
        
        # ใช้ JavaScript Click เพื่อความชัวร์ (บางทีมีอะไรบัง Click ธรรมดาจะ error)
        driver.execute_script("arguments[0].click();", read_more_btn)
        print("-> กดปุ่ม 'ข้อมูลเพิ่มเติม' สำเร็จ")
        time.sleep(1) # รอข้อความขยาย
    except Exception:
        # ถ้าหาปุ่มไม่เจอ หรือกดไม่ได้ (เช่น ข้อความสั้นอยู่แล้ว) ก็ปล่อยผ่าน
        pass

    # -------------------------------------------------------
    # 2. เริ่มดูดข้อมูลด้วย BeautifulSoup
    # -------------------------------------------------------
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = {}

    # --- A. Title ---
    try:
        # ตัด class ยาวๆ ออก ใช้แค่ id ก็ระบุได้แม่นยำแล้วครับ
        data['title'] = soup.select_one('#title_modal_more').get_text(strip=True)
    except:
        data['title'] = None

    # --- B. Description ---
    try:
        # ตัด col-lg... ออก ใช้แค่ class หลักที่เป็นชื่อเฉพาะ
        data['description'] = soup.select_one('.box_show_detail_descript').get_text(strip=True)
    except:
        data['description'] = None

    # --- C. Price & Price per Sqm ---
    try:
        price_box = soup.select_one('.box_price_mb')
        
        # Price: หา span class price-detail -> เข้าไปเอา b -> เอา text
        # ผลลัพธ์จะเป็น "฿10,500,000" หรือ "10,500,000"
        price_raw = price_box.select_one('.price-detail b').get_text(strip=True)
        data['price'] = price_raw.replace('฿', '').replace(',', '') # Clean ให้เป็นตัวเลขล้วน
        
        # Price per Sqm: หา class price_cal_area_text_modal
        pp_sqm_raw = price_box.select_one('.price_cal_area_text_modal').get_text(strip=True)
        # ผลลัพธ์จะเป็น "(229,458 บ./ตร.ม.)" -> ตัดวงเล็บและข้อความออก
        data['price_per_sqm'] = pp_sqm_raw.replace('(', '').replace(')', '').replace('บ./ตร.ม.', '').replace(',', '').strip()
        
    except:
        data['price'] = None
        data['price_per_sqm'] = None

    # --- D. Loop หาข้อมูลใน List (พื้นที่, ชั้น, ห้องนอน, ห้องน้ำ) ---
    # ข้อมูลพวกนี้อยู่ในโครงสร้างคล้ายกัน คือเป็น row > title | text
    # เราจะวน Loop หาเพื่อความแม่นยำ
    
    rows = soup.select('.detail-list-property') # หาแถวรายการทั้งหมด
    
    # ตั้งค่า Default เป็น None ไว้ก่อน
    data['usable_area'] = None
    data['floor'] = None
    data['bedroom'] = None
    data['restroom'] = None

    for row in rows:
        try:
            title_span = row.select_one('.detail-property-list-title')
            value_span = row.select_one('.detail-property-list-text')
            
            if not title_span or not value_span:
                continue
                
            title_text = title_span.get_text(strip=True)
            value_text = value_span.get_text(strip=True)
            
            # เช็คเงื่อนไขตาม Keyword
            if "พื้นที่ใช้สอย" in title_text:
                data['usable_area'] = value_text.replace('ตร.ม.', '').strip()
                
            elif "ชั้นของห้อง" in title_text or "ชั้นที่" in title_text:
                data['floor'] = value_text
                
            elif "ห้องนอน" in title_text:
                data['bedroom'] = value_text
            
            # แก้ไข: ใน Prompt คุณเขียน "ห้องนอน" ซ้ำในส่วน restroom 
            # ผมแก้ Logic เป็น "ห้องน้ำ" ให้นะครับ เพื่อความถูกต้อง
            elif "ห้องน้ำ" in title_text: 
                data['restroom'] = value_text
                
        except:
            continue

    data['url'] = url
    return data

# ==========================================
# Main Execution
# ==========================================
if __name__ == "__main__":
    # ตั้งค่า Driver
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # ปิดบรรทัดนี้ถ้าอยากเห็นหน้าจอ browser
    driver = uc.Chrome(options=options)

    # ตัวอย่าง URL คอนโด (ใส่ URL จริงลงไปลองเทสตรงนี้)
    test_urls = [
        "https://www.livinginsider.com/livingdetail/condo/id/123456.html", # <--- เปลี่ยนเป็น URL จริงที่ต้องการเทส
    ]
    
    # *หมายเหตุ: ปกติคุณต้องเขียน Loop ดึง URL จากหน้า Search มาใส่ใน list นี้ก่อน
    
    results = []
    
    try:
        for url in test_urls:
            if "livinginsider.com" in url: # เช็คว่าเป็น Link จริงๆ ไม่ใช่ Link มั่ว
                info = scrape_condo_detail(driver, url)
                print(info)
                results.append(info)
    finally:
        driver.quit()
        
        # Save ลง Excel/CSV
        if results:
            df = pd.DataFrame(results)
            df.to_csv('living_insider_data.csv', index=False, encoding='utf-8-sig')
            print("Saved to CSV successfully.")