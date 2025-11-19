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
    แล้วหา span ที่มี keyword ที่กำหนด
    จากนั้นคืนค่า text ของ span ตัวถัดไป (ที่เป็นค่าข้อมูล)
    """
    rows = soup.find_all("div", class_="detail-list-property")
    for row in rows:
        title_span = row.find("span", class_="detail-property-list-title")
        if title_span and keyword in title_span.get_text(strip=True):
            value_span = row.find("span", class_="detail-property-list-text")
            if value_span:
                return value_span.get_text(strip=True)
    return None

def scrape_living_insider():
    # 1. ตั้งค่า Driver (ใช้ undetected เพื่อหลบ Bot)
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # ช่วงแรกแนะนำให้ปิดบรรทัดนี้ เพื่อดูการทำงาน
    driver = uc.Chrome(options=options)

    # URL หน้ารวมประกาศ (ตามที่คุณส่งมา)
    main_url = "https://www.livinginsider.com/searchword/Condo/Buysell/1/รวมประกาศ-ขาย-คอนโด.html"
    
    print(f"🚀 กำลังเข้าสู่หน้าหลัก: {main_url}")
    driver.get(main_url)
    time.sleep(5) # รอเว็บโหลด

    # เก็บ Link ของแต่ละคอนโด
    all_links = []
    soup_main = BeautifulSoup(driver.page_source, 'html.parser')
    
    # หา class "item-desc" ตามที่บอก
    items = soup_main.find_all('div', class_='item-desc')
    
    print(f"🔎 เจอประกาศทั้งหมด {len(items)} รายการในหน้านี้")
    
    for item in items:
        # หา <a> ที่ซ่อนอยู่ใน item-desc (ปกติจะเป็น tag a ที่คลุม title หรือกดเข้าไปได้)
        a_tag = item.find_parent('a') # หรือหา a ที่อยู่ใน div นี้
        if not a_tag:
            a_tag = item.find('a')
            
        if a_tag and 'href' in a_tag.attrs:
            all_links.append(a_tag['href'])

    # ตัวแปรเก็บข้อมูลทั้งหมด
    data_list = []

    # 2. Loop เข้าไปทีละ Link
    # (Demo: ลองดึงแค่ 5 อันแรกพอนะครับ ถ้าจะเอาจริงให้ลบ [:5] ออก)
    for i, link in enumerate(all_links[:5]): 
        full_url = link if link.startswith("http") else f"https://www.livinginsider.com{link}"
        print(f"[{i+1}/{len(all_links)}] กำลังดึงข้อมูล: {full_url}")
        
        try:
            driver.get(full_url)
            time.sleep(3) # รอหน้าโหลด

            # --- Step: กดปุ่ม "ข้อมูลเพิ่มเติม..." ---
            try:
                # พยายามหาปุ่มและกด (ถ้ามี)
                # ใช้ XPath หา span ที่มี text 'ข้อมูลเพิ่มเติม...' ภายใต้ class font_title_more
                more_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'font_title_more')]//span[contains(text(), 'ข้อมูลเพิ่มเติม')]"))
                )
                more_btn.click()
                time.sleep(1) # รอ text ขยายออกมา
            except Exception:
                pass # ถ้าไม่มีปุ่ม หรือกดไม่ได้ ก็ปล่อยผ่าน (บางที text มันมาครบแล้วแค่ซ่อน css)

            # --- Step: ดึงข้อมูลด้วย BeautifulSoup ---
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # 1. Title
            title_div = soup.find("div", id="title_modal_more")
            title = title_div.get_text(strip=True) if title_div else None

            # 2. Description (ตัด class ยาวๆ ออก เหลือแค่ตัวหลัก)
            desc_div = soup.find("div", class_="box_show_detail_descript")
            description = desc_div.get_text(strip=True) if desc_div else None

            # 3. Price
            price_div = soup.find("div", class_="box_price_mb")
            price = None
            if price_div:
                # หา <b> ที่อยู่ใน span class price-detail
                price_span = price_div.find("span", class_="price-detail")
                if price_span:
                    price_b = price_span.find("b")
                    if price_b:
                        price = price_b.get_text(strip=True) # จะได้ "฿105,000,000"

            # 4. Price per Sq.m.
            price_sqm = None
            if price_div:
                # หา class เฉพาะเจาะจง "price_cal_area_text_modal"
                sqm_span = price_div.find("span", class_="price_cal_area_text_modal")
                if sqm_span:
                    price_sqm = sqm_span.get_text(strip=True) # จะได้ "(229,458 บ./ตร.ม.)"

            # 5. ใช้ Helper Function ดึงพวก list property
            usable_area = get_property_value(soup, "พื้นที่ใช้สอย")
            floor = get_property_value(soup, "ชั้น") # ใช้คำสั้นๆ ว่า "ชั้น" จะคลุมทั้ง "ชั้นที่" และ "ชั้นของห้อง"
            bedroom = get_property_value(soup, "ห้องนอน")
            restroom = get_property_value(soup, "ห้องน้ำ") # **แก้จาก ห้องนอน เป็น ห้องน้ำ**

            # เก็บลง Dictionary
            row_data = {
                "URL": full_url,
                "Title": title,
                "Price": price,
                "Price_Per_Sqm": price_sqm,
                "Usable_Area": usable_area,
                "Floor": floor,
                "Bedroom": bedroom,
                "Restroom": restroom,
                "Description": description # อันนี้ยาวหน่อย ระวังตอนดูใน Excel
            }
            
            data_list.append(row_data)
            print(f"   ✅ ได้ข้อมูล: {title[:30]}... | ราคา: {price}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    driver.quit()

    # 3. Save to CSV
    df = pd.DataFrame(data_list)
    df.to_csv("living_insider_data.csv", index=False, encoding="utf-8-sig")
    print("\n🎉 เสร็จสิ้น! บันทึกไฟล์ living_insider_data.csv เรียบร้อย")

if __name__ == "__main__":
    scrape_living_insider()