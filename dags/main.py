import time
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Helper Function: หาค่าจาก list รายละเอียด (เช่น ชั้น, พื้นที่) ---
def get_property_value(soup, keyword):
    """
    ค้นหา div ที่มี class 'detail-list-property'
    แล้วค้นหา div ย่อย 'detail-col-property-list' ที่มี keyword อยู่ข้างใน
    """
    property_groups = soup.find_all("div", class_="detail-list-property")
    
    for group in property_groups:
        # ค้นหาเฉพาะรายการย่อยที่ระบุ: detail-col-property-list
        property_items = group.find_all("div", class_="detail-col-property-list")
        
        for item in property_items:
            # ค้นหา span ที่เป็น title ภายในรายการย่อยนั้น
            title_span = item.find("span", class_="detail-property-list-title")
            
            # ตรวจสอบว่า keyword ที่ต้องการอยู่ในชื่อข้อมูลหรือไม่
            if title_span and keyword in title_span.get_text(strip=True):
                # ดึงค่าข้อมูล (span ที่เป็น text)
                value_span = item.find("span", class_="detail-property-list-text")
                if value_span:
                    return value_span.get_text(strip=True)
                    
    return None

def scrape_living_insider():
    # 1. ตั้งค่า Driver
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    driver = uc.Chrome(options=options)

    # URL หน้ารวมประกาศ
    main_url = "https://www.livinginsider.com/searchword/Condo/Buysell/1/รวมประกาศ-ขาย-คอนโด.html"
    
    print(f"🚀 กำลังเข้าสู่หน้าหลัก: {main_url}")
    driver.get(main_url)
    time.sleep(5) 

    # เก็บ Link ของแต่ละคอนโด
    all_links = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "item-desc"))
        )
    except Exception as e:
        print(f"Error: ไม่พบประกาศในหน้าหลัก: {e}")
        driver.quit()
        return

    soup_main = BeautifulSoup(driver.page_source, 'html.parser')
    
    items = soup_main.find_all('div', class_='item-desc')
    
    unique_links = set()
    for item in items:
        a_tag = item.find_parent('a') 
        if a_tag and 'href' in a_tag.attrs:
            unique_links.add(a_tag['href'])
        a_tag_inner = item.find('a')
        if a_tag_inner and 'href' in a_tag_inner.attrs:
             unique_links.add(a_tag_inner['href'])
    
    all_links = list(unique_links)
    
    print(f"🔎 เจอประกาศทั้งหมด {len(all_links)} รายการในหน้านี้ (รวม link ที่ไม่ซ้ำ)")
    
    data_list = []

    # 2. Loop เข้าไปทีละ Link
    # (Demo: ลองดึงแค่ 5 อันแรกพอนะครับ ถ้าจะเอาจริงให้ลบ [:5] ออก)
    for i, link in enumerate(all_links[:5]): 
        full_url = link if link.startswith("http") else f"https://www.livinginsider.com{link}"
        print(f"\n--- [{i+1}/{len(all_links)}] กำลังดึงข้อมูล: {full_url} ---")
        
        try:
            driver.get(full_url)
            
            # ใช้ WebDriverWait รอให้ Title หลักแสดงผล (จากคลาสใหม่)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "text_project_detail_green"))
            )
            
            # --- Step: ดึงข้อมูลด้วย BeautifulSoup (รอบแรก) ---
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 1. Title (ใหม่)
            title_div = soup.find("span", class_="text_project_detail_green")
            title = title_div.get_text(strip=True) if title_div else None
            
            # 2. Publish Date (ใหม่)
            date_span = soup.find("span", class_="lv-small-font grey font_10_date font_sarabun")
            publish_date = None
            if date_span:
                # ตัดคำว่า "สร้างเมื่อ" ออก (หรือคำที่คล้ายกัน)
                date_text = date_span.get_text(strip=True)
                publish_date = date_text.replace("สร้างเมื่อ", "").replace("ปรับปรุง", "").strip()


            # --- Step: กดปุ่ม "ข้อมูลเพิ่มเติม..." (ถ้ามี) เพื่อให้ข้อมูลอื่นแสดงผล ---
            try:
                more_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'font_title_more')]//span[contains(text(), 'ข้อมูลเพิ่มเติม')]"))
                )
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(1)
                print("   🔔 กดปุ่ม 'ข้อมูลเพิ่มเติม...' แล้ว")
                
                # อัพเดท soup หลังจากกดปุ่ม
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            except Exception:
                pass # ถ้าไม่มีปุ่ม หรือกดไม่ได้ ก็ใช้ soup เดิม

            # 3. Price
            price_div = soup.find("div", class_="box_price_mb")
            price = None
            if price_div:
                price_b = price_div.find("span", class_="price-detail")
                if price_b:
                    price_b_inner = price_b.find("b")
                    if price_b_inner:
                        price = price_b_inner.get_text(strip=True)

            # 4. Price per Sq.m.
            price_sqm = None
            if price_div:
                sqm_span = price_div.find("span", class_="price_cal_area_text_modal")
                if sqm_span:
                    price_sqm = sqm_span.get_text(strip=True)

            # 5. ใช้ Helper Function ดึงพวก list property (ต้องรอหลังกดปุ่ม)
            usable_area = get_property_value(soup, "พื้นที่ใช้สอย")
            floor = get_property_value(soup, "ชั้น") 
            bedroom = get_property_value(soup, "ห้องนอน")
            restroom = get_property_value(soup, "ห้องน้ำ") 

            # เก็บลง Dictionary
            row_data = {
                "URL": full_url,
                "Title": title,
                "Publish_Date": publish_date,  # เพิ่มคอลัมน์ใหม่
                "Price": price,
                "Price_Per_Sqm": price_sqm,
                "Usable_Area": usable_area,
                "Floor": floor,
                "Bedroom": bedroom,
                "Restroom": restroom
            }
            
            data_list.append(row_data)
            print(f"   ✅ ได้ข้อมูล: {title[:30]}... | ราคา: {price} | วันที่: {publish_date}")

        except Exception as e:
            print(f"   ❌ Error ในการดึงข้อมูล {full_url}: {e}")
            continue

    driver.quit()

    # 3. Save to CSV
    df = pd.DataFrame(data_list)
    df.to_csv("living_insider_data_updated.csv", index=False, encoding="utf-8-sig")
    print(f"\n🎉 เสร็จสิ้น! บันทึกไฟล์ living_insider_data_updated.csv เรียบร้อย ทั้งหมด {len(df)} รายการ")

if __name__ == "__main__":
    scrape_living_insider()